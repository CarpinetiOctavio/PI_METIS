import logging
import os
from datetime import datetime, timezone

import aiosmtplib
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from metis.auth.dependencies import get_current_user
from metis.auth.email import generate_verification_token, send_verification_email
from metis.auth.jwt import create_access_token
from metis.db import get_db
from metis.db.models import User
from metis.schemas.auth import LoginRequest, RegisterRequest, UserMe, VerifyRequest

logger = logging.getLogger(__name__)

_FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
_ENV = os.environ.get("ENV", "development")
_COOKIE_SECURE = _ENV == "production"
_COOKIE_NAME = "access_token"

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# LIMITACIÓN: dict en memoria de proceso. Funciona con un solo
# worker (desarrollo y V1.0 en intranet). En producción con
# múltiples workers cada worker tiene su propio dict — el token
# generado en worker A no lo encuentra worker B.
# Solución futura: mover tokens a Redis o BD post-M5.
_pending_tokens: dict[str, str] = {}


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "AUTH_EMAIL_ALREADY_REGISTERED",
                    "mensaje": "El email ya está registrado",
                }
            },
        )

    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    token = generate_verification_token()

    user = User(
        email=body.email,
        nombre=body.nombre,
        password_hash=password_hash,
        email_verified=False,
    )

    # Mandar el mail antes de tocar la sesión de BD acota la ventana de falla
    # (no "la elimina": Gmail y Postgres no comparten transacción). Si el envío
    # falla, no se persiste nada — el usuario puede reintentar el registro sin
    # quedar huérfano (email_verified=False, sin vía de reenvío). Sigue existiendo
    # el caso más raro de que el mail salga bien y el commit() de abajo falle
    # después — se acepta esa ventana residual conscientemente.
    try:
        await send_verification_email(body.email, token)
    except (aiosmtplib.SMTPException, RuntimeError):
        logger.exception("Fallo al enviar mail de verificación a %s", body.email)
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "codigo": "AUTH_VERIFICATION_EMAIL_FAILED",
                    "mensaje": "No pudimos enviar el mail de verificación, intentá registrarte de nuevo en unos minutos.",
                }
            },
        )

    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        # Race: otro registro con el mismo email commiteó entre el SELECT de
        # arriba y este commit. El unique constraint de User.email lo atrapa acá.
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "AUTH_EMAIL_ALREADY_REGISTERED",
                    "mensaje": "El email ya está registrado",
                }
            },
        )

    # Registrar el token solo tras commit exitoso: si el mail salió pero el
    # commit falló arriba, no queda un token vivo apuntando a un usuario
    # inexistente — quien clickee el link recibe AUTH_INVALID_TOKEN y puede
    # re-registrarse limpio.
    _pending_tokens[token] = body.email

    return {
        "ok": True,
        "mensaje": "Cuenta creada. Revisá tu mail para verificar la dirección.",
    }


@router.post("/verify")
async def verify(body: VerifyRequest, db: AsyncSession = Depends(get_db)):
    email = _pending_tokens.pop(body.token, None)
    if email is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "AUTH_INVALID_TOKEN",
                    "mensaje": "Token inválido o expirado",
                }
            },
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "codigo": "AUTH_USER_NOT_FOUND",
                    "mensaje": "Usuario no encontrado",
                }
            },
        )

    user.email_verified = True
    await db.commit()
    return {"ok": True}


@router.post("/login")
async def login(
    body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not bcrypt.checkpw(
        body.password.encode(), user.password_hash.encode()
    ):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "codigo": "AUTH_INVALID_CREDENTIALS",
                    "mensaje": "Email o contraseña incorrectos",
                }
            },
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "codigo": "AUTH_EMAIL_NOT_VERIFIED",
                    "mensaje": "Verificá tu email antes de iniciar sesión",
                }
            },
        )

    user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()

    token = create_access_token({"sub": user.email})
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=_COOKIE_SECURE,
    )
    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=_COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=UserMe)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

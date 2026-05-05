import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metis.auth.dependencies import get_current_user
from metis.auth.google import exchange_code_for_email, get_google_auth_url, is_ucc_email
from metis.auth.jwt import create_access_token
from metis.db import get_db
from metis.db.models import User
from metis.schemas.auth import UserMe

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ENV = os.getenv("ENV", "development")
COOKIE_SECURE = ENV == "production"
COOKIE_NAME = "access_token"

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/google")
def login_google():
    return RedirectResponse(url=get_google_auth_url())


@router.get("/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        email, nombre = await exchange_code_for_email(code)
    except Exception:
        raise HTTPException(status_code=400, detail="Error al autenticar con Google")

    if not is_ucc_email(email):
        raise HTTPException(status_code=403, detail="Solo cuentas @ucc.edu.ar")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email, nombre=nombre)
        db.add(user)
    else:
        from datetime import datetime, timezone

        user.last_login = datetime.now(timezone.utc)
        if nombre and not user.nombre:
            user.nombre = nombre

    await db.commit()

    token = create_access_token({"sub": email})
    response = RedirectResponse(url=FRONTEND_URL)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
    )
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse(url=FRONTEND_URL)
    response.delete_cookie(key=COOKIE_NAME)
    return response


@router.get("/me", response_model=UserMe)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

"""Tokens de un solo uso para la recuperación de contraseña (DECISIÓN 085).

El token en claro (`secrets.token_urlsafe`) solo existe en el mail; la base guarda su SHA-256. Las
operaciones no hacen `commit`: lo hace el endpoint, para que el cambio de contraseña y el consumo
del token queden en la misma transacción.
"""

import hashlib
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from metis.db.models import AuthToken

PURPOSE_PASSWORD_RESET = "password_reset"

# Vigencia del link. Una hora alcanza para abrir el mail y es corta si la casilla queda abierta.
RESET_TTL = timedelta(minutes=int(os.environ.get("RESET_TOKEN_TTL_MINUTES", "60")))
# Mínimo entre dos mails de recuperación para la misma cuenta: evita usar el endpoint (que no
# pide sesión) para llenarle la casilla a alguien o agotar el cupo del relay SMTP de la UCC.
RESET_COOLDOWN = timedelta(seconds=int(os.environ.get("RESET_COOLDOWN_SECONDS", "60")))


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def issue_reset_token(db: AsyncSession, user_id: uuid.UUID) -> str | None:
    """Crea un token de recuperación para `user_id` y devuelve el valor en claro.

    Devuelve None, sin crear nada, si ya se pidió uno hace menos de RESET_COOLDOWN. Invalida los
    tokens anteriores todavía vivos: solo el último link que se mandó sirve.
    """
    ahora = _ahora()

    ultimo = await db.execute(
        select(func.max(AuthToken.created_at)).where(
            AuthToken.user_id == user_id,
            AuthToken.purpose == PURPOSE_PASSWORD_RESET,
        )
    )
    creado = ultimo.scalar_one_or_none()
    if creado is not None and ahora - creado < RESET_COOLDOWN:
        return None

    await _invalidar_vivos(db, user_id, ahora)

    token = secrets.token_urlsafe(32)
    db.add(
        AuthToken(
            user_id=user_id,
            purpose=PURPOSE_PASSWORD_RESET,
            token_hash=hash_token(token),
            expires_at=ahora + RESET_TTL,
            created_at=ahora,
        )
    )
    await db.commit()
    return token


async def consume_reset_token(db: AsyncSession, token: str) -> uuid.UUID | None:
    """Marca el token como usado y devuelve el id del usuario, o None si no sirve.

    Un solo UPDATE condicional: el mismo link usado dos veces a la vez lo consume una sola
    (el segundo UPDATE no encuentra fila libre).
    """
    ahora = _ahora()
    resultado = await db.execute(
        update(AuthToken)
        .where(
            AuthToken.token_hash == hash_token(token),
            AuthToken.purpose == PURPOSE_PASSWORD_RESET,
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > ahora,
        )
        .values(used_at=ahora)
        .returning(AuthToken.user_id)
    )
    return resultado.scalar_one_or_none()


async def invalidate_reset_tokens(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Deja sin efecto los links de recuperación que sigan vivos de `user_id`."""
    await _invalidar_vivos(db, user_id, _ahora())


async def _invalidar_vivos(
    db: AsyncSession, user_id: uuid.UUID, ahora: datetime
) -> None:
    await db.execute(
        update(AuthToken)
        .where(
            AuthToken.user_id == user_id,
            AuthToken.purpose == PURPOSE_PASSWORD_RESET,
            AuthToken.used_at.is_(None),
        )
        .values(used_at=ahora)
    )

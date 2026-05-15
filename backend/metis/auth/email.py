"""
Envío de mail de verificación de cuenta.

ESTADO: mock de desarrollo — loggea el token en consola en lugar de enviarlo.
PENDIENTE: cuando IT provea la cuenta metis-noreply@ucc.edu.ar y el App Password,
reemplazar send_verification_email por implementación real con aiosmtplib.
Ver decisions-log.md — DECISIÓN 004.
"""

import logging
import os
import secrets

logger = logging.getLogger(__name__)

_FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


async def send_verification_email(email: str, token: str) -> None:
    # TODO: reemplazar con aiosmtplib cuando IT provea credenciales SMTP.
    # Variables requeridas: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD.
    verify_url = f"{_FRONTEND_URL}/auth/verify?token={token}"
    logger.info(
        "[MOCK SMTP] Token de verificación para %s — URL: %s",
        email,
        verify_url,
    )

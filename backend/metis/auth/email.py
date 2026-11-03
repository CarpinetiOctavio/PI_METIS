"""
Envío de mails de la cuenta (verificación y recuperación de contraseña) via aiosmtplib.

Ver docs/decisiones/decision004.md — DECISIÓN 004 (mecanismo de envío)
y docs/decisiones/decision034.md — DECISIÓN 034 (separación de identidad
de autenticación y remitente). SMTP_STARTTLS: docs/decisiones/decision049.md.
Recuperación de contraseña: docs/decisiones/decision085.md.
"""

import os
import secrets
from email.message import EmailMessage

import aiosmtplib

_FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
_SMTP_HOST = os.environ.get("SMTP_HOST")
_SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
_SMTP_USER = os.environ.get("SMTP_USER")
_SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
_SMTP_FROM_ADDRESS = os.environ.get("SMTP_FROM_ADDRESS")
# Segundos máximos para conectar y para cada comando SMTP. aiosmtplib espera 60 por defecto, más que el
# navegador: un relay lento se veía como un timeout del registro sin código (despliegue UCC, 30/10/2026).
# Con 20 s el error sale como AUTH_VERIFICATION_EMAIL_FAILED, con el detalle en el log del backend.
_SMTP_TIMEOUT = float(os.environ.get("SMTP_TIMEOUT", "20"))
# DECISIÓN 049: STARTTLS se puede apagar para un servidor de captura local (Mailpit en
# desarrollo, E2E y CI, que no habla TLS). Default "true": producción no cambia.
_SMTP_STARTTLS = os.environ.get("SMTP_STARTTLS", "true").strip().lower() not in (
    "false",
    "0",
    "no",
)


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def _validar_config() -> None:
    if not _SMTP_HOST or not _SMTP_USER or not _SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_HOST, SMTP_USER y SMTP_PASSWORD deben estar configurados "
            "en el entorno — ver .env.example."
        )
    if not _SMTP_FROM_ADDRESS:
        raise RuntimeError(
            "SMTP_FROM_ADDRESS debe estar configurado en el entorno — ver "
            ".env.example. No usar SMTP_USER como remitente: es la identidad "
            "de autenticación del relay, no necesariamente una dirección "
            "de mail válida."
        )


async def _enviar(message: EmailMessage) -> None:
    await aiosmtplib.send(
        message,
        hostname=_SMTP_HOST,
        port=_SMTP_PORT,
        username=_SMTP_USER,
        password=_SMTP_PASSWORD,
        start_tls=_SMTP_STARTTLS,
        timeout=_SMTP_TIMEOUT,
    )


async def send_verification_email(email: str, token: str) -> None:
    _validar_config()

    verify_url = f"{_FRONTEND_URL}/auth/verify?token={token}"

    message = EmailMessage()
    message["From"] = _SMTP_FROM_ADDRESS
    message["To"] = email
    message["Subject"] = "METIS — Verificá tu cuenta"
    message.set_content(
        "Verificá tu cuenta ingresando al siguiente link:\n\n"
        f"{verify_url}\n\n"
        "Si no creaste esta cuenta, podés ignorar este mail."
    )

    await _enviar(message)


async def send_password_reset_email(
    email: str, token: str, vigencia_minutos: int
) -> None:
    """Mail con el link para elegir una contraseña nueva (DECISIÓN 085)."""
    _validar_config()

    reset_url = f"{_FRONTEND_URL}/auth/reset-password?token={token}"

    message = EmailMessage()
    message["From"] = _SMTP_FROM_ADDRESS
    message["To"] = email
    message["Subject"] = "METIS: Restablecé tu contraseña"
    message.set_content(
        "Recibimos un pedido para restablecer la contraseña de tu cuenta de METIS.\n\n"
        "Para elegir una nueva, ingresá al siguiente link. Vale por "
        f"{vigencia_minutos} minutos y se puede usar una sola vez:\n\n"
        f"{reset_url}\n\n"
        "Si no lo pediste vos, ignorá este mail: tu contraseña no cambia."
    )

    await _enviar(message)

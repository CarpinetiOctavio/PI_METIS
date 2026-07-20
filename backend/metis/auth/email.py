"""
Envío de mail de verificación de cuenta.

ESTADO: mock de desarrollo — loggea el token en consola en lugar de enviarlo.
PENDIENTE: cuando IT provea la cuenta metis-noreply@ucc.edu.ar y el App Password,
reemplazar send_verification_email por implementación real con aiosmtplib.
Ver docs/decisiones/decision004.md — DECISIÓN 004.
"""

import os
import secrets

_FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


async def send_verification_email(email: str, token: str) -> None:
    # TODO: eliminar este print y reemplazar con envío real
    # via aiosmtplib cuando IT provea credenciales SMTP.
    # Ver docs/decisiones/decision004.md — DECISIÓN 004.
    verify_url = f"{_FRONTEND_URL}/auth/verify?token={token}"
    print(
        f"[MOCK SMTP] Token de verificación para {email} — URL: {verify_url}",
        flush=True,
    )

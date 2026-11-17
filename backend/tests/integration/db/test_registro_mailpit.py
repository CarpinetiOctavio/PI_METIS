"""
Integración externa: registro → mail de verificación → verificación → login, contra un servidor
SMTP real (Mailpit, DECISIÓN 049) y PostgreSQL real. B4 del plan del TP de Calidad.

Nada de este flujo está mockeado: `auth/email.py` manda el mensaje con `aiosmtplib` a Mailpit, el
test lo lee por la API HTTP de Mailpit, extrae el link y sigue el flujo por HTTP como lo haría el
usuario. Es el único test que ejercita el envío real; los de `tests/unit/auth/` usan dobles.

Requiere en el entorno, además de la base de `conftest.py`:
- `SMTP_HOST`/`SMTP_PORT` apuntando a Mailpit, `SMTP_STARTTLS=false`, credenciales de relleno;
- `MAILPIT_URL` (API HTTP de Mailpit, por ejemplo `http://localhost:8025`).
Sin `MAILPIT_URL` se saltea; con `METIS_REQUIRE_MAILPIT=1` (CI) falla.
"""

import re
import uuid

import httpx
import pytest
from sqlalchemy import delete

from metis.db import get_db
from metis.db.models import User
from metis.main import app
from tests.integration.db._mailpit import esperar_mail

pytestmark = pytest.mark.integration

_LINK = re.compile(r"/auth/verify\?token=([A-Za-z0-9_\-]+)")


async def test_registro_verificacion_y_login_con_mail_real(db, mailpit_url):
    # Arrange
    email = f"registro-{uuid.uuid4().hex[:10]}@ucc.edu.ar"
    password = "password-registro-1"

    async def _db_de_test():
        yield db

    app.dependency_overrides[get_db] = _db_de_test
    try:
        async with (
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as api,
            httpx.AsyncClient(base_url=mailpit_url, timeout=10) as mailpit,
        ):
            # Act
            registro = await api.post(
                "/api/v1/auth/register",
                json={"email": email, "password": password, "nombre": "Registro E2E"},
            )
            login_antes = await api.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            )
            texto = await esperar_mail(mailpit, email)
            token = _LINK.search(texto).group(1)
            verificacion = await api.post("/api/v1/auth/verify", json={"token": token})
            reuso = await api.post("/api/v1/auth/verify", json={"token": token})
            login = await api.post(
                "/api/v1/auth/login", json={"email": email, "password": password}
            )
            me = await api.get("/api/v1/auth/me")
    finally:
        app.dependency_overrides.pop(get_db, None)
        await db.rollback()
        await db.execute(delete(User).where(User.email == email))
        await db.commit()

    # Assert
    assert registro.status_code == 201
    assert login_antes.status_code == 403
    assert login_antes.json()["error"]["codigo"] == "AUTH_EMAIL_NOT_VERIFIED"
    assert verificacion.status_code == 200
    assert reuso.status_code == 400
    assert reuso.json()["error"]["codigo"] == "AUTH_INVALID_TOKEN"
    assert login.status_code == 200
    assert me.json()["email"] == email
    assert me.json()["email_verified"] is True

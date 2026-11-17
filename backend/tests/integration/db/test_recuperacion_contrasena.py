"""
Recuperación de contraseña (DECISIÓN 085) contra PostgreSQL real y, en el flujo de punta a punta,
contra un servidor SMTP real (Mailpit, DECISIÓN 049).

`test_flujo_completo_con_mail_real` pide Mailpit (como test_registro_mailpit.py); el resto no lo
necesita: crean el token con `issue_reset_token` o dejan que el envío falle sin SMTP, que es
justamente lo que el endpoint tiene que tragarse sin cambiar la respuesta.
"""

import re
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import httpx
import pytest
from sqlalchemy import delete, func, select

from metis.auth import tokens
from metis.auth.tokens import PURPOSE_PASSWORD_RESET, hash_token, issue_reset_token
from metis.db import get_db
from metis.db.models import AuthToken, User
from metis.main import app
from tests.integration.db._datos import PASSWORD
from tests.integration.db._mailpit import esperar_mail

pytestmark = pytest.mark.integration

_LINK = re.compile(r"/auth/reset-password\?token=([A-Za-z0-9_\-]+)")
_NUEVA = "clave-nueva-de-test-2"


def _ahora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@pytest.fixture
async def api(db):
    async def _db_de_test():
        yield db

    app.dependency_overrides[get_db] = _db_de_test
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as cliente:
            yield cliente
    finally:
        app.dependency_overrides.pop(get_db, None)


async def _login(api, email, password):
    return await api.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


async def _reset(api, token, password=_NUEVA):
    return await api.post(
        "/api/v1/auth/reset-password", json={"token": token, "password": password}
    )


async def _filas(db, user_id):
    r = await db.execute(select(AuthToken).where(AuthToken.user_id == user_id))
    return r.scalars().all()


async def test_flujo_completo_con_mail_real(api, db, crear_usuario, mailpit_url):
    # Arrange
    usuario = await crear_usuario("recupera")

    async with httpx.AsyncClient(base_url=mailpit_url, timeout=10) as mailpit:
        # Act
        pedido = await api.post(
            "/api/v1/auth/forgot-password", json={"email": usuario.email}
        )
        texto = await esperar_mail(mailpit, usuario.email)
        token = _LINK.search(texto).group(1)
        cambio = await _reset(api, token)
        reuso = await _reset(api, token, "otra-clave-de-test-3")
        login_nuevo = await _login(api, usuario.email, _NUEVA)
        login_viejo = await _login(api, usuario.email, PASSWORD)
    filas = await _filas(db, usuario.id)

    # Assert
    assert pedido.status_code == 200
    assert cambio.status_code == 200
    assert reuso.status_code == 400
    assert reuso.json()["error"]["codigo"] == "AUTH_RESET_TOKEN_INVALID"
    assert login_nuevo.status_code == 200
    assert login_viejo.status_code == 401
    # En la base queda el hash, nunca el token que viajó en el mail.
    assert [f.token_hash for f in filas] == [hash_token(token)]
    assert token not in {f.token_hash for f in filas}
    assert filas[0].used_at is not None


async def test_forgot_responde_lo_mismo_exista_o_no_la_cuenta_y_sin_cuenta_no_guarda_nada(
    api, db, crear_usuario
):
    # Arrange
    usuario = await crear_usuario("existe")
    inexistente = f"nadie-{uuid.uuid4().hex[:10]}@ucc.edu.ar"
    antes = (await db.execute(select(func.count()).select_from(AuthToken))).scalar_one()

    # Act
    con_cuenta = await api.post(
        "/api/v1/auth/forgot-password", json={"email": usuario.email}
    )
    sin_cuenta = await api.post(
        "/api/v1/auth/forgot-password", json={"email": inexistente}
    )
    despues = (
        await db.execute(select(func.count()).select_from(AuthToken))
    ).scalar_one()

    # Assert
    assert con_cuenta.status_code == sin_cuenta.status_code == 200
    assert con_cuenta.json() == sin_cuenta.json()
    assert len(await _filas(db, usuario.id)) == 1  # el envío sin SMTP falla en silencio
    assert despues == antes + 1  # ninguna fila para el mail inexistente


async def test_dos_pedidos_seguidos_no_crean_un_segundo_token(api, db, crear_usuario):
    # Arrange
    usuario = await crear_usuario("cooldown")

    # Act
    primero = await api.post(
        "/api/v1/auth/forgot-password", json={"email": usuario.email}
    )
    segundo = await api.post(
        "/api/v1/auth/forgot-password", json={"email": usuario.email}
    )

    # Assert
    assert primero.json() == segundo.json()
    assert len(await _filas(db, usuario.id)) == 1


async def test_un_pedido_nuevo_invalida_el_link_anterior(
    api, db, crear_usuario, monkeypatch
):
    # Arrange
    monkeypatch.setattr(tokens, "RESET_COOLDOWN", timedelta(0))
    usuario = await crear_usuario("invalida")
    viejo = await issue_reset_token(db, usuario.id)
    nuevo = await issue_reset_token(db, usuario.id)

    # Act
    con_el_viejo = await _reset(api, viejo)
    con_el_nuevo = await _reset(api, nuevo)

    # Assert
    assert viejo != nuevo
    assert con_el_viejo.status_code == 400
    assert con_el_nuevo.status_code == 200


async def test_token_vencido_no_sirve(api, db, crear_usuario):
    # Arrange
    usuario = await crear_usuario("vencido")
    token = "token-vencido-de-prueba"
    db.add(
        AuthToken(
            user_id=usuario.id,
            purpose=PURPOSE_PASSWORD_RESET,
            token_hash=hash_token(token),
            expires_at=_ahora() - timedelta(minutes=1),
            created_at=_ahora() - timedelta(hours=2),
        )
    )
    await db.commit()

    # Act
    r = await _reset(api, token)

    # Assert
    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == "AUTH_RESET_TOKEN_INVALID"
    assert (
        await _login(api, usuario.email, PASSWORD)
    ).status_code == 200  # la clave no cambió


async def test_token_inexistente_responde_400(api):
    r = await _reset(api, "token-que-nunca-existio")

    assert r.status_code == 400
    assert r.json()["error"]["codigo"] == "AUTH_RESET_TOKEN_INVALID"


async def test_clave_corta_responde_422_y_no_gasta_el_token(api, db, crear_usuario):
    # Arrange
    usuario = await crear_usuario("corta")
    token = await issue_reset_token(db, usuario.id)

    # Act
    corta = await _reset(api, token, "corta")
    valida = await _reset(api, token)

    # Assert
    assert corta.status_code == 422
    assert valida.status_code == 200


async def test_restablecer_verifica_una_cuenta_que_quedo_sin_verificar(api, db):
    # Arrange: el caso H8 (DECISIÓN 034): se registró y el backend se reinició antes de verificar.
    email = f"sinverificar-{uuid.uuid4().hex[:10]}@ucc.edu.ar"
    usuario = User(
        email=email,
        nombre="Sin verificar",
        password_hash=bcrypt.hashpw(
            PASSWORD.encode(), bcrypt.gensalt(rounds=4)
        ).decode(),
        email_verified=False,
    )
    db.add(usuario)
    await db.commit()
    try:
        antes = await _login(api, email, PASSWORD)
        token = await issue_reset_token(db, usuario.id)

        # Act
        cambio = await _reset(api, token)
        despues = await _login(api, email, _NUEVA)
    finally:
        await db.rollback()
        await db.execute(delete(User).where(User.email == email))
        await db.commit()

    # Assert
    assert antes.status_code == 403
    assert antes.json()["error"]["codigo"] == "AUTH_EMAIL_NOT_VERIFIED"
    assert cambio.status_code == 200
    assert despues.status_code == 200


async def test_borrar_el_usuario_borra_sus_tokens(db, crear_usuario):
    # Arrange
    usuario = await crear_usuario("cascada")
    await issue_reset_token(db, usuario.id)
    assert len(await _filas(db, usuario.id)) == 1

    # Act
    await db.execute(delete(User).where(User.id == usuario.id))
    await db.commit()

    # Assert
    assert await _filas(db, usuario.id) == []

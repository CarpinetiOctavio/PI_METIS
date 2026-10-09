"""
Tests unitarios de POST /auth/verify, /auth/login, /auth/logout y GET /auth/me (router.py).
Complementan test_router_register.py; mismo patrón: se llama a la función del endpoint con la
sesión de BD mockeada, sin conexión real. B2 del plan del TP de Calidad. Estructura
Arrange-Act-Assert explícita.

Mismo cuidado de import que test_router_register.py: `from metis.auth.router import <nombre>`,
nunca vía el atributo `router` del paquete (es el APIRouter, no el submódulo).
"""

from unittest.mock import AsyncMock, MagicMock

import bcrypt
import pytest
from fastapi import HTTPException, Response

from metis.auth.jwt import is_valid_token
from metis.auth.router import _pending_tokens, login, logout, me, verify
from metis.schemas.auth import LoginRequest, VerifyRequest

_EMAIL = "legajo@ucc.edu.ar"
_PASSWORD = "password123"
# rounds=4: el mínimo de bcrypt; el costo no es lo que se prueba acá.
_HASH = bcrypt.hashpw(_PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode()


def _db(usuario) -> MagicMock:
    db = MagicMock()
    resultado = MagicMock()
    resultado.scalar_one_or_none.return_value = usuario
    db.execute = AsyncMock(return_value=resultado)
    db.commit = AsyncMock()
    return db


def _usuario(verificado: bool = True) -> MagicMock:
    return MagicMock(
        email=_EMAIL, password_hash=_HASH, email_verified=verificado, last_login=None
    )


@pytest.fixture(autouse=True)
def _pending_tokens_aislado():
    # Mismo criterio que test_router_register.py: limpiar in-place, sin rebind.
    _pending_tokens.clear()
    yield _pending_tokens
    _pending_tokens.clear()


# --- verify -------------------------------------------------------------------------------------


@pytest.mark.unit
async def test_verify_marca_el_email_como_verificado_y_consume_el_token():
    # Arrange
    _pending_tokens["tok-123"] = _EMAIL
    usuario = _usuario(verificado=False)
    db = _db(usuario)

    # Act
    respuesta = await verify(VerifyRequest(token="tok-123"), db=db)

    # Assert
    assert respuesta == {"ok": True}
    assert usuario.email_verified is True
    db.commit.assert_awaited_once()
    assert "tok-123" not in _pending_tokens


@pytest.mark.unit
async def test_verify_token_desconocido_responde_400_sin_tocar_la_bd():
    # Arrange
    db = _db(None)
    cuerpo = VerifyRequest(token="no-existe")

    # Act
    with pytest.raises(HTTPException) as exc:
        await verify(cuerpo, db=db)

    # Assert
    assert exc.value.status_code == 400
    assert exc.value.detail["error"]["codigo"] == "AUTH_INVALID_TOKEN"
    db.execute.assert_not_called()


@pytest.mark.unit
async def test_verify_token_usado_dos_veces_falla_la_segunda():
    # Arrange
    _pending_tokens["tok-123"] = _EMAIL
    db = _db(_usuario(verificado=False))
    await verify(VerifyRequest(token="tok-123"), db=db)
    cuerpo = VerifyRequest(token="tok-123")

    # Act
    with pytest.raises(HTTPException) as exc:
        await verify(cuerpo, db=db)

    # Assert
    assert exc.value.detail["error"]["codigo"] == "AUTH_INVALID_TOKEN"


@pytest.mark.unit
async def test_verify_usuario_borrado_responde_404():
    # Arrange
    _pending_tokens["tok-123"] = _EMAIL
    db = _db(None)
    cuerpo = VerifyRequest(token="tok-123")

    # Act
    with pytest.raises(HTTPException) as exc:
        await verify(cuerpo, db=db)

    # Assert
    assert exc.value.status_code == 404
    assert exc.value.detail["error"]["codigo"] == "AUTH_USER_NOT_FOUND"
    db.commit.assert_not_called()


# --- login --------------------------------------------------------------------------------------


@pytest.mark.unit
async def test_login_correcto_setea_cookie_httponly_y_registra_last_login():
    # Arrange
    usuario = _usuario()
    db = _db(usuario)
    response = Response()

    # Act
    respuesta = await login(
        LoginRequest(email=_EMAIL, password=_PASSWORD), response, db=db
    )

    # Assert
    assert respuesta == {"ok": True}
    cookie = response.headers["set-cookie"]
    assert cookie.startswith("access_token=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    token = cookie.split(";")[0].split("=", 1)[1]
    assert is_valid_token(token)["sub"] == _EMAIL
    assert usuario.last_login is not None
    db.commit.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("usuario", "password"),
    [
        pytest.param(None, _PASSWORD, id="email-inexistente"),
        pytest.param("EXISTE", "otra-clave-1", id="password-incorrecta"),
    ],
)
async def test_login_credenciales_invalidas_responde_401_sin_cookie(usuario, password):
    # Arrange: el mismo código para los dos casos, sin revelar si el email existe
    db = _db(_usuario() if usuario == "EXISTE" else None)
    response = Response()
    cuerpo = LoginRequest(email=_EMAIL, password=password)

    # Act
    with pytest.raises(HTTPException) as exc:
        await login(cuerpo, response, db=db)

    # Assert
    assert exc.value.status_code == 401
    assert exc.value.detail["error"]["codigo"] == "AUTH_INVALID_CREDENTIALS"
    assert "set-cookie" not in response.headers


@pytest.mark.unit
async def test_login_email_sin_verificar_responde_403():
    # Arrange
    db = _db(_usuario(verificado=False))
    response = Response()
    cuerpo = LoginRequest(email=_EMAIL, password=_PASSWORD)

    # Act
    with pytest.raises(HTTPException) as exc:
        await login(cuerpo, response, db=db)

    # Assert
    assert exc.value.status_code == 403
    assert exc.value.detail["error"]["codigo"] == "AUTH_EMAIL_NOT_VERIFIED"
    db.commit.assert_not_called()


# --- logout y me --------------------------------------------------------------------------------


@pytest.mark.unit
def test_logout_borra_la_cookie_aunque_no_haya_sesion():
    # Arrange
    response = Response()

    # Act
    respuesta = logout(response)

    # Assert
    assert respuesta == {"ok": True}
    cookie = response.headers["set-cookie"]
    assert cookie.startswith('access_token=""') or cookie.startswith("access_token=;")
    assert "Max-Age=0" in cookie


@pytest.mark.unit
async def test_me_devuelve_el_usuario_autenticado():
    # Arrange
    usuario = _usuario()

    # Act
    resultado = await me(current_user=usuario)

    # Assert
    assert resultado is usuario

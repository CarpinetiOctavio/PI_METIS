"""
Tests unitarios de metis.auth.dependencies — get_current_user (CU-01, JWT requerido) y
get_optional_user (la misma ruta sirve a CU-01 y CU-02 según haya cookie). B2 del plan del TP
de Calidad. Se llama a las dependencias directamente con un Request y una sesión de BD
mockeados: no abren conexión real. Estructura Arrange-Act-Assert explícita.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from metis.auth.dependencies import COOKIE_NAME, get_current_user, get_optional_user
from metis.auth.jwt import create_access_token


def _request(token: str | None) -> MagicMock:
    request = MagicMock()
    request.cookies = {} if token is None else {COOKIE_NAME: token}
    return request


def _db(usuario) -> MagicMock:
    db = MagicMock()
    resultado = MagicMock()
    resultado.scalar_one_or_none.return_value = usuario
    db.execute = AsyncMock(return_value=resultado)
    return db


def _token_sin_sub() -> str:
    return create_access_token({"rol": "docente"})


# --- get_current_user ---------------------------------------------------------------------------


@pytest.mark.unit
async def test_get_current_user_devuelve_el_usuario_de_la_cookie():
    # Arrange
    usuario = MagicMock(email="legajo@ucc.edu.ar")
    request = _request(create_access_token({"sub": "legajo@ucc.edu.ar"}))
    db = _db(usuario)

    # Act
    resultado = await get_current_user(request, db=db)

    # Assert
    assert resultado is usuario
    db.execute.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("token", "usuario", "detalle"),
    [
        pytest.param(None, None, "No autenticado", id="sin-cookie"),
        pytest.param(
            "adulterado", None, "Token inválido o expirado", id="token-adulterado"
        ),
        pytest.param("SIN_SUB", None, "Token inválido", id="token-sin-sub"),
        pytest.param("VALIDO", None, "Usuario no encontrado", id="usuario-inexistente"),
    ],
)
async def test_get_current_user_responde_401(token, usuario, detalle):
    # Arrange
    if token == "SIN_SUB":
        token = _token_sin_sub()
    elif token == "VALIDO":
        token = create_access_token({"sub": "borrado@ucc.edu.ar"})
    request = _request(token)
    db = _db(usuario)

    # Act
    with pytest.raises(HTTPException) as exc:
        await get_current_user(request, db=db)

    # Assert
    assert exc.value.status_code == 401
    assert exc.value.detail == detalle


@pytest.mark.unit
async def test_get_current_user_no_consulta_la_bd_sin_cookie():
    # Arrange
    db = _db(None)

    # Act
    with pytest.raises(HTTPException):
        await get_current_user(_request(None), db=db)

    # Assert
    db.execute.assert_not_called()


# --- get_optional_user --------------------------------------------------------------------------


@pytest.mark.unit
async def test_get_optional_user_devuelve_el_usuario_con_cookie_valida():
    # Arrange
    usuario = MagicMock(email="legajo@ucc.edu.ar")
    request = _request(create_access_token({"sub": "legajo@ucc.edu.ar"}))

    # Act
    resultado = await get_optional_user(request, db=_db(usuario))

    # Assert
    assert resultado is usuario


@pytest.mark.unit
@pytest.mark.parametrize(
    "token",
    [
        pytest.param(None, id="sin-cookie"),
        pytest.param("adulterado", id="token-adulterado"),
        pytest.param("SIN_SUB", id="token-sin-sub"),
    ],
)
async def test_get_optional_user_degrada_a_anonimo(token):
    # Arrange: sin sesión válida el análisis sigue como CU-02, no responde 401
    if token == "SIN_SUB":
        token = _token_sin_sub()
    db = _db(MagicMock())

    # Act
    resultado = await get_optional_user(_request(token), db=db)

    # Assert
    assert resultado is None
    db.execute.assert_not_called()


@pytest.mark.unit
async def test_get_optional_user_devuelve_none_si_el_usuario_ya_no_existe():
    # Arrange
    request = _request(create_access_token({"sub": "borrado@ucc.edu.ar"}))

    # Act
    resultado = await get_optional_user(request, db=_db(None))

    # Assert
    assert resultado is None

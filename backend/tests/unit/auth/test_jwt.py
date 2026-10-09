"""
Tests unitarios de metis.auth.jwt — firma y validación del JWT de sesión (B2 del plan del TP de
Calidad, docs/plan-tp-calidad-software.md). Estructura Arrange-Act-Assert explícita.
"""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from metis.auth.jwt import (
    ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
    decode_access_token,
    is_valid_token,
)


@pytest.mark.unit
def test_create_access_token_conserva_el_sub_y_agrega_exp():
    # Arrange
    datos = {"sub": "legajo@ucc.edu.ar"}

    # Act
    token = create_access_token(datos)
    payload = decode_access_token(token)

    # Assert
    assert payload["sub"] == "legajo@ucc.edu.ar"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


@pytest.mark.unit
def test_create_access_token_no_muta_el_dict_recibido():
    # Arrange
    datos = {"sub": "legajo@ucc.edu.ar"}

    # Act
    create_access_token(datos)

    # Assert
    assert datos == {"sub": "legajo@ucc.edu.ar"}


@pytest.mark.unit
def test_is_valid_token_devuelve_el_payload_de_un_token_propio():
    # Arrange
    token = create_access_token({"sub": "legajo@ucc.edu.ar"})

    # Act
    payload = is_valid_token(token)

    # Assert
    assert payload is not None
    assert payload["sub"] == "legajo@ucc.edu.ar"


@pytest.mark.unit
@pytest.mark.parametrize(
    "token",
    [
        pytest.param("no-es-un-jwt", id="texto-cualquiera"),
        pytest.param("", id="vacio"),
        pytest.param(
            jwt.encode({"sub": "x@ucc.edu.ar"}, "otra-clave", algorithm=ALGORITHM),
            id="firmado-con-otra-clave",
        ),
        pytest.param(
            jwt.encode(
                {
                    "sub": "x@ucc.edu.ar",
                    "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
                },
                JWT_SECRET_KEY,
                algorithm=ALGORITHM,
            ),
            id="vencido",
        ),
    ],
)
def test_is_valid_token_devuelve_none_ante_un_token_invalido(token):
    # Arrange: el token parametrizado

    # Act
    payload = is_valid_token(token)

    # Assert
    assert payload is None

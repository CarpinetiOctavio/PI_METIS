"""
Tests unitarios de metis.auth.tokens (DECISIÓN 085) — la sesión de BD se mockea, no hay conexión
real. La unicidad del hash y el UPDATE condicional contra Postgres real los cubre
tests/integration/db/test_auth_tokens.py.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from metis.auth import tokens
from metis.auth.tokens import (
    PURPOSE_PASSWORD_RESET,
    RESET_COOLDOWN,
    RESET_TTL,
    consume_reset_token,
    hash_token,
    invalidate_reset_tokens,
    issue_reset_token,
)


def _ahora():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _resultado(valor):
    r = MagicMock()
    r.scalar_one_or_none.return_value = valor
    return r


def _db(*resultados):
    db = MagicMock()
    db.execute = AsyncMock(side_effect=list(resultados))
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.mark.unit
def test_hash_token_es_sha256_en_hex_y_no_devuelve_el_token():
    h = hash_token("abc")
    assert len(h) == 64
    assert h == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert "abc" not in h


@pytest.mark.unit
async def test_issue_sin_pedido_previo_crea_el_token_y_guarda_solo_el_hash():
    user_id = uuid.uuid4()
    # 1) max(created_at) sin filas, 2) UPDATE que invalida los vivos.
    db = _db(_resultado(None), MagicMock())

    token = await issue_reset_token(db, user_id)

    assert token and len(token) >= 40
    db.add.assert_called_once()
    fila = db.add.call_args.args[0]
    assert fila.user_id == user_id
    assert fila.purpose == PURPOSE_PASSWORD_RESET
    assert fila.token_hash == hash_token(token)
    assert token not in (fila.token_hash, str(fila.purpose))
    assert fila.used_at is None
    assert fila.expires_at - fila.created_at == RESET_TTL
    db.commit.assert_awaited_once()


@pytest.mark.unit
async def test_issue_dentro_del_cooldown_no_crea_nada():
    db = _db(_resultado(_ahora() - RESET_COOLDOWN + timedelta(seconds=10)))

    assert await issue_reset_token(db, uuid.uuid4()) is None

    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    assert db.execute.await_count == 1  # solo la consulta del último pedido


@pytest.mark.unit
async def test_issue_pasado_el_cooldown_crea_otro_token():
    db = _db(_resultado(_ahora() - RESET_COOLDOWN - timedelta(seconds=5)), MagicMock())

    assert await issue_reset_token(db, uuid.uuid4()) is not None
    db.add.assert_called_once()


@pytest.mark.unit
async def test_issue_genera_tokens_distintos():
    a = await issue_reset_token(_db(_resultado(None), MagicMock()), uuid.uuid4())
    b = await issue_reset_token(_db(_resultado(None), MagicMock()), uuid.uuid4())
    assert a != b


@pytest.mark.unit
async def test_consume_devuelve_el_usuario_cuando_el_update_encuentra_el_token():
    user_id = uuid.uuid4()
    db = _db(_resultado(user_id))

    assert await consume_reset_token(db, "token-valido") == user_id
    db.execute.assert_awaited_once()


@pytest.mark.unit
async def test_consume_devuelve_none_si_el_token_no_sirve():
    # Inexistente, ya usado o vencido: el UPDATE condicional no devuelve fila.
    db = _db(_resultado(None))

    assert await consume_reset_token(db, "token-malo") is None


@pytest.mark.unit
async def test_consume_busca_por_hash_y_no_por_el_token_en_claro():
    db = _db(_resultado(None))

    await consume_reset_token(db, "token-secreto")

    consulta = db.execute.call_args.args[0]
    compilada = consulta.compile()
    assert hash_token("token-secreto") in compilada.params.values()
    assert "token-secreto" not in compilada.params.values()


@pytest.mark.unit
async def test_invalidate_ejecuta_un_update_sin_commit():
    db = _db(MagicMock())

    await invalidate_reset_tokens(db, uuid.uuid4())

    db.execute.assert_awaited_once()
    db.commit.assert_not_awaited()


@pytest.mark.unit
def test_los_defaults_de_vigencia_y_cooldown():
    assert tokens.RESET_TTL == timedelta(minutes=60)
    assert tokens.RESET_COOLDOWN == timedelta(seconds=60)

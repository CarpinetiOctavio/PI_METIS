"""
Exclusiones guardadas en el historial (DECISIÓN 080, bloque C2 de
docs/plan-revision-manual-21-10-2026.md), contra PostgreSQL real.

Guardar, listar y quitar; la misma selección no se duplica; índices inválidos;
pertenencia (404 a otro usuario, también por HTTP); y el resultado original y las
decisiones quedan intactos (DECISIÓN 062).
"""

import uuid

import httpx
import numpy as np
import pytest

from metis.core.pipeline.exclusiones import ExclusionInvalidaError
from metis.db import get_db
from metis.main import app
from metis.services.analysis_service import get_analysis_by_id, get_history
from metis.services.exclusiones_service import (
    ExclusionNoEncontradaError,
    guardar_exclusion,
    quitar_exclusion,
)
from tests.integration._sse_helpers import parse_sse, run_stream
from tests.integration.db._datos import PASSWORD

pytestmark = pytest.mark.integration

# La misma serie que test_persistencia.py: el stream no pausa (Chow sin atípico).
_SERIE = np.random.default_rng(seed=9).uniform(10, 100, size=50).tolist()


async def _correr(db, user_id) -> str:
    filas = [f"{1970 + i},{v}" for i, v in enumerate(_SERIE)]
    csv = ("anio,caudal\n" + "\n".join(filas) + "\n").encode()
    gen, _ = run_stream(csv, columna_x="anio", user_id=user_id, db=db)
    eventos = [parse_sse(e) async for e in gen]
    assert eventos[-1][0] == "complete"
    return eventos[-1][1]["analysis_id"]


async def test_guardar_listar_y_quitar_sin_tocar_el_resultado(db, crear_usuario):
    # Arrange
    usuario = await crear_usuario()
    analysis_id = await _correr(db, usuario.id)
    antes = await get_analysis_by_id(analysis_id, usuario.id, db)

    # Act
    guardada = await guardar_exclusion(analysis_id, usuario.id, [13, 3], db)
    detalle = await get_analysis_by_id(analysis_id, usuario.id, db)
    (item,) = await get_history(usuario.id, db)
    quitada = await quitar_exclusion(analysis_id, usuario.id, guardada["id"], db)
    despues = await get_analysis_by_id(analysis_id, usuario.id, db)

    # Assert: años y valores salen del análisis persistido, índices ordenados
    serie = antes["etapa1"]["datos"]["serie_efectiva"]
    assert guardada["indices"] == [3, 13]
    assert guardada["puntos"] == [
        {"indice": 3, "periodo": 1973, "valor": serie[3]},
        {"indice": 13, "periodo": 1983, "valor": serie[13]},
    ]
    assert guardada["alfa"] == 0.05
    assert guardada["cramer_particion"] == "default"
    assert detalle["exclusiones"] == [guardada]
    assert item["exclusiones_guardadas"] == 1
    assert quitada is True
    assert despues["exclusiones"] == []
    # DECISIÓN 062: ni el resultado ni el registro de decisiones cambian.
    for clave in ("etapa1", "etapa2", "decisiones"):
        assert detalle[clave] == antes[clave]
        assert despues[clave] == antes[clave]


async def test_la_misma_seleccion_no_se_duplica(db, crear_usuario):
    usuario = await crear_usuario()
    analysis_id = await _correr(db, usuario.id)

    primera = await guardar_exclusion(analysis_id, usuario.id, [3, 13], db)
    segunda = await guardar_exclusion(analysis_id, usuario.id, [13, 3], db)
    otra = await guardar_exclusion(analysis_id, usuario.id, [4], db)

    detalle = await get_analysis_by_id(analysis_id, usuario.id, db)
    assert segunda == primera
    assert [e["id"] for e in detalle["exclusiones"]] == [primera["id"], otra["id"]]


# Bordes de la validación (docs/calidad/casos-de-prueba.md, VL-09 y VL-10): la
# serie de prueba tiene 50 datos, índices 0 a 49.
@pytest.mark.parametrize(
    "indices",
    [[-1], [50], [3, 3], [], list(range(50))],
    ids=[
        "VL-09a índice -1",
        "VL-09d índice n",
        "VL-09e repetido",
        "VL-10a ninguno",
        "VL-10c los n (vacía la serie)",
    ],
)
async def test_indices_invalidos(db, crear_usuario, indices):
    usuario = await crear_usuario()
    analysis_id = await _correr(db, usuario.id)

    with pytest.raises(ExclusionInvalidaError):
        await guardar_exclusion(analysis_id, usuario.id, indices, db)

    detalle = await get_analysis_by_id(analysis_id, usuario.id, db)
    assert detalle["exclusiones"] == []


@pytest.mark.parametrize(
    "indices",
    [[0], [49], list(range(49))],
    ids=["VL-09b índice 0", "VL-09c índice n-1", "VL-10b n-1 puntos (queda uno)"],
)
async def test_indices_en_el_borde_validos(db, crear_usuario, indices):
    usuario = await crear_usuario()
    analysis_id = await _correr(db, usuario.id)

    guardada = await guardar_exclusion(analysis_id, usuario.id, indices, db)

    assert guardada["indices"] == indices


async def test_otro_usuario_no_guarda_ni_quita(db, crear_usuario):
    duenio = await crear_usuario("duenio")
    otro = await crear_usuario("otro")
    analysis_id = await _correr(db, duenio.id)
    guardada = await guardar_exclusion(analysis_id, duenio.id, [3], db)

    assert await guardar_exclusion(analysis_id, otro.id, [4], db) is None
    assert await quitar_exclusion(analysis_id, otro.id, guardada["id"], db) is False
    with pytest.raises(ExclusionNoEncontradaError):
        await quitar_exclusion(analysis_id, duenio.id, str(uuid.uuid4()), db)
    detalle = await get_analysis_by_id(analysis_id, duenio.id, db)
    assert detalle["exclusiones"] == [guardada]


async def test_por_http_con_login_real(db, crear_usuario):
    # Arrange: login real (bcrypt + JWT en cookie) y la app completa con esta sesión
    duenio = await crear_usuario("duenio")
    otro = await crear_usuario("otro")
    analysis_id = await _correr(db, duenio.id)
    url = f"/api/v1/history/{analysis_id}/exclusiones"

    async def _db_de_test():
        yield db

    app.dependency_overrides[get_db] = _db_de_test
    transporte = httpx.ASGITransport(app=app)
    try:
        async with (
            httpx.AsyncClient(transport=transporte, base_url="http://test") as duenio_c,
            httpx.AsyncClient(transport=transporte, base_url="http://test") as otro_c,
        ):
            for cliente, usuario in ((duenio_c, duenio), (otro_c, otro)):
                login = await cliente.post(
                    "/api/v1/auth/login",
                    json={"email": usuario.email, "password": PASSWORD},
                )
                assert login.status_code == 200

            # Act
            guardada = await duenio_c.post(url, json={"indices_excluidos": [3]})
            invalida = await duenio_c.post(url, json={"indices_excluidos": [99]})
            ajena = await otro_c.post(url, json={"indices_excluidos": [4]})
            detalle_ajeno = await otro_c.get(f"/api/v1/history/{analysis_id}")
            id_guardada = guardada.json()["id"]
            quitar_ajena = await otro_c.delete(f"{url}/{id_guardada}")
            quitar_inexistente = await duenio_c.delete(f"{url}/{uuid.uuid4()}")
            quitar = await duenio_c.delete(f"{url}/{id_guardada}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    # Assert
    assert guardada.status_code == 200
    assert invalida.status_code == 400
    assert invalida.json()["error"]["codigo"] == "CONTRACT_EXCLUSION_INVALID"
    assert ajena.status_code == 404
    assert ajena.json()["error"]["codigo"] == "ANALYSIS_NOT_FOUND"
    assert detalle_ajeno.status_code == 404
    assert quitar_ajena.status_code == 404
    assert quitar_ajena.json()["error"]["codigo"] == "ANALYSIS_NOT_FOUND"
    assert quitar_inexistente.status_code == 404
    assert quitar_inexistente.json()["error"]["codigo"] == "ANALYSIS_EXCLUSION_NOT_FOUND"
    assert quitar.status_code == 200

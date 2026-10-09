"""
Integración contra PostgreSQL real (B3 del plan del TP de Calidad).

Cubre compromisos de `.claude/rules/testing.md` ("Tests de integración del pipeline") que hasta
ahora solo se probaban con la sesión de BD mockeada:
- persistencia correcta en BD para CU-01;
- ausencia de persistencia para CU-02;
- historial: listado, archivado y desarchivado (DECISIÓN 048);
- pertenencia: un análisis ajeno responde 404, también por HTTP.

Estructura Arrange-Act-Assert explícita.
"""

import httpx
import numpy as np
import pytest
from sqlalchemy import func, select

from metis.db import get_db
from metis.db.models import Analysis, AnalysisResult
from metis.main import app
from metis.services.analysis_service import (
    archive_analysis,
    get_analysis_by_id,
    get_history,
    unarchive_analysis,
)
from tests.integration._sse_helpers import parse_sse, run_stream
from tests.integration.db._datos import PASSWORD

pytestmark = pytest.mark.integration

# Misma serie que test_etapa2_stream_distribution_decision.py (seed=9, uniform(10, 100), n=50):
# todas las pruebas de Etapa 1 aprueban y Chow no detecta atípico, así el stream no pausa.
_SERIE = np.random.default_rng(seed=9).uniform(10, 100, size=50).tolist()


def _csv() -> bytes:
    filas = [f"{1970 + i},{v}" for i, v in enumerate(_SERIE)]
    return ("anio,caudal\n" + "\n".join(filas) + "\n").encode()


async def _correr(db, user_id) -> str | None:
    """Corre el stream completo y devuelve el analysis_id del evento `complete`."""
    gen, _ = run_stream(_csv(), columna_x="anio", user_id=user_id, db=db)
    eventos = [parse_sse(e) async for e in gen]
    assert eventos[-1][0] == "complete"
    return eventos[-1][1]["analysis_id"]


async def _contar_analisis(db) -> int:
    return (await db.execute(select(func.count()).select_from(Analysis))).scalar_one()


async def test_cu01_persiste_el_analisis_y_su_resultado(db, crear_usuario):
    # Arrange
    usuario = await crear_usuario()

    # Act
    analysis_id = await _correr(db, usuario.id)

    # Assert
    assert analysis_id is not None
    analisis = (
        await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    ).scalar_one()
    resultado = (
        await db.execute(
            select(AnalysisResult).where(AnalysisResult.analysis_id == analysis_id)
        )
    ).scalar_one()
    assert analisis.user_id == usuario.id
    assert analisis.serie == pytest.approx(_SERIE)
    assert analisis.configuracion["nombre_archivo"] == "serie.csv"
    assert resultado.etapa1["nivel_confianza"] in ("validado", "con_warnings")
    assert resultado.etapa2 is None


async def test_cu02_anonimo_no_persiste_nada(db):
    # Arrange
    antes = await _contar_analisis(db)

    # Act
    analysis_id = await _correr(db, user_id=None)

    # Assert
    assert analysis_id is None
    assert await _contar_analisis(db) == antes


async def test_historial_lista_archiva_y_desarchiva(db, crear_usuario):
    # Arrange
    usuario = await crear_usuario()
    analysis_id = await _correr(db, usuario.id)

    # Act
    visibles = await get_history(usuario.id, db)
    archivado = await archive_analysis(analysis_id, usuario.id, db)
    tras_archivar = await get_history(usuario.id, db)
    con_archivados = await get_history(usuario.id, db, incluir_archivados=True)
    desarchivado = await unarchive_analysis(analysis_id, usuario.id, db)
    tras_desarchivar = await get_history(usuario.id, db)

    # Assert
    assert [a["id"] for a in visibles] == [analysis_id]
    assert archivado is True
    assert tras_archivar == []
    assert con_archivados[0]["archivado_at"] is not None
    assert desarchivado is True
    assert tras_desarchivar[0]["archivado_at"] is None


async def test_un_analisis_ajeno_no_se_lee_ni_se_archiva(db, crear_usuario):
    # Arrange
    duenio = await crear_usuario("duenio")
    otro = await crear_usuario("otro")
    analysis_id = await _correr(db, duenio.id)

    # Act
    leido_por_otro = await get_analysis_by_id(analysis_id, otro.id, db)
    archivado_por_otro = await archive_analysis(analysis_id, otro.id, db)
    leido_por_duenio = await get_analysis_by_id(analysis_id, duenio.id, db)

    # Assert
    assert leido_por_otro is None
    assert archivado_por_otro is False
    assert leido_por_duenio is not None
    assert leido_por_duenio["configuracion"]["nombre_archivo"] == "serie.csv"


async def test_get_history_por_http_responde_404_a_otro_usuario(db, crear_usuario):
    # Arrange: login real (bcrypt + JWT en cookie) y la app completa con esta sesión de BD
    duenio = await crear_usuario("duenio")
    otro = await crear_usuario("otro")
    analysis_id = await _correr(db, duenio.id)

    async def _db_de_test():
        yield db

    app.dependency_overrides[get_db] = _db_de_test
    transporte = httpx.ASGITransport(app=app)
    try:
        async with (
            httpx.AsyncClient(
                transport=transporte, base_url="http://test"
            ) as como_otro,
            httpx.AsyncClient(
                transport=transporte, base_url="http://test"
            ) as como_duenio,
        ):
            for cliente, usuario in ((como_otro, otro), (como_duenio, duenio)):
                login = await cliente.post(
                    "/api/v1/auth/login",
                    json={"email": usuario.email, "password": PASSWORD},
                )
                assert login.status_code == 200

            # Act
            respuesta_otro = await como_otro.get(f"/api/v1/history/{analysis_id}")
            respuesta_duenio = await como_duenio.get(f"/api/v1/history/{analysis_id}")
    finally:
        app.dependency_overrides.pop(get_db, None)

    # Assert
    assert respuesta_otro.status_code == 404
    assert respuesta_duenio.status_code == 200
    assert respuesta_duenio.json()["id"] == analysis_id

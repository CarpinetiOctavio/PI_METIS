"""
Primer test de tests/integration/ (Bloque A6 del plan de implementación de
Etapa 2 — el directorio existía vacío desde feature/services-sse).

Corre stream_analysis() de punta a punta con etapas=[1, 2] sobre una serie
de fixture, consume los eventos SSE en el orden real, manda la decisión de
distribución a mitad de camino (igual que haría el cliente real vía
POST /analysis/distribution-decision) y verifica que el stream se
desbloquea solo y termina con result_etapa2_eventos + complete.

CU-02 (anónimo, user_id=None): no persiste, así que no necesita una BD de
test real — es la forma más barata de probar el cableado nuevo de punta a
punta. La persistencia real (CU-01) queda para un test de integración
aparte, no es lo que este bloque "estrena".
"""

import numpy as np
import pytest

from metis.services import session_store
from metis.services.analysis_service import registrar_distribution_decision
from tests.integration._sse_helpers import parse_sse, run_stream

# Misma serie que SERIE_VALIDADA en test_pipeline_etapa1.py/test_full_pipeline.py
# — numpy seed=9, uniform(10, 100), n=50. Todas las pruebas de Etapa 1
# aprueban sin warnings y sin atípico de Chow, así que este test ejercita
# únicamente la pausa nueva de Etapa 2, no la de Chow (ya cubierta en
# tests/unit/services/test_analysis_service.py).
_rng = np.random.default_rng(seed=9)
_SERIE_VALIDADA = _rng.uniform(10, 100, size=50).tolist()

_PERIODOS = [2, 5, 10, 25, 50, 100, 200, 500]


def _csv_de_serie_valida() -> bytes:
    filas = [f"{1970 + i},{valor}" for i, valor in enumerate(_SERIE_VALIDADA)]
    return ("anio,caudal\n" + "\n".join(filas) + "\n").encode()


def _run_etapa2(**overrides):
    """run_stream() con los kwargs propios de este archivo: columna de año
    puro y etapas=[1, 2] salvo que el test pida otra cosa."""
    return run_stream(
        _csv_de_serie_valida(),
        columna_x="anio",
        etapas=overrides.pop("etapas", [1, 2]),
        **overrides,
    )


def _primera_ajustada(ranking: list[dict]) -> dict:
    """La primera distribución del ranking que efectivamente ajustó
    (mejor_eea no nulo) — igual que elegiría un usuario real desde
    RankingPage."""
    return next(d for d in ranking if d["mejor_eea"] is not None)


@pytest.mark.integration
async def test_stream_con_etapas_1_2_pausa_en_ranking_y_termina_con_eventos():
    gen, session_id = _run_etapa2()

    tipos_recibidos: list[str] = []
    resultado_decision = None

    async for evento_crudo in gen:
        tipo, data = parse_sse(evento_crudo)
        tipos_recibidos.append(tipo)

        if tipo == "result_etapa2_ranking":
            elegida = _primera_ajustada(data["ranking"])
            resultado_decision = await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=_PERIODOS,
            )

    assert resultado_decision == {"ok": True, "pipeline_continua": True}

    # Secuencia real, en orden: Etapa 1 completa, luego el progress de
    # Etapa 2, el ranking (donde pausó), los eventos de diseño y el cierre.
    assert "result_etapa1" in tipos_recibidos
    assert "result_etapa2_ranking" in tipos_recibidos
    assert "result_etapa2_eventos" in tipos_recibidos
    assert tipos_recibidos[-1] == "complete"
    assert tipos_recibidos.index("result_etapa2_ranking") < tipos_recibidos.index(
        "result_etapa2_eventos"
    )
    assert tipos_recibidos.index("result_etapa1") < tipos_recibidos.index(
        "result_etapa2_ranking"
    )

    # Sesión limpiada al terminar (finally de stream_analysis).
    assert session_store.get_session(session_id) is None


@pytest.mark.integration
async def test_result_etapa2_eventos_trae_los_periodos_retorno_pedidos():
    gen, session_id = _run_etapa2()

    payload_eventos = None
    async for evento_crudo in gen:
        tipo, data = parse_sse(evento_crudo)
        if tipo == "result_etapa2_ranking":
            elegida = _primera_ajustada(data["ranking"])
            await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=_PERIODOS,
            )
        elif tipo == "result_etapa2_eventos":
            payload_eventos = data

    assert payload_eventos is not None
    assert [
        e["periodo_retorno"] for e in payload_eventos["eventos_diseno"]
    ] == _PERIODOS
    # Serie sin ceros y distribución con parámetros ajustados -> ningún
    # evento debería quedar en None para este fixture.
    assert all(e["valor"] is not None for e in payload_eventos["eventos_diseno"])


@pytest.mark.integration
async def test_result_etapa2_ranking_trae_puntos_empiricos():
    # Bloque C — insumo del gráfico de ajuste, independiente de la
    # distribución elegida: tiene que viajar en el evento de ranking, antes
    # de que el usuario decida nada.
    gen, session_id = _run_etapa2()

    payload_ranking = None
    async for evento_crudo in gen:
        tipo, data = parse_sse(evento_crudo)
        if tipo == "result_etapa2_ranking":
            payload_ranking = data
            elegida = _primera_ajustada(data["ranking"])
            await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=_PERIODOS,
            )

    assert payload_ranking is not None
    assert len(payload_ranking["puntos_empiricos"]) == len(_SERIE_VALIDADA)
    primer_punto = payload_ranking["puntos_empiricos"][0]
    assert {"valor", "periodo_retorno", "probabilidad"} == set(primer_punto)
    # Convención de probabilidades_weibull: m=1 es el máximo, orden DESC.
    assert primer_punto["valor"] == pytest.approx(max(_SERIE_VALIDADA))


@pytest.mark.integration
async def test_result_etapa2_eventos_trae_curva_ajuste_continua():
    gen, session_id = _run_etapa2()

    payload_eventos = None
    async for evento_crudo in gen:
        tipo, data = parse_sse(evento_crudo)
        if tipo == "result_etapa2_ranking":
            elegida = _primera_ajustada(data["ranking"])
            await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=_PERIODOS,
            )
        elif tipo == "result_etapa2_eventos":
            payload_eventos = data

    assert payload_eventos is not None
    curva = payload_eventos["curva_ajuste"]
    # Muestreo denso (60 puntos) — no los mismos T discretos que pidió el
    # usuario, mucho más fino, para dibujar la curva completa.
    assert len(curva) == 60
    assert len(curva) > len(payload_eventos["eventos_diseno"])
    # Orden creciente de T, en escala log — geomspace ya lo garantiza, pero
    # es la propiedad que el gráfico necesita para no tener que reordenar.
    periodos_curva = [p["periodo_retorno"] for p in curva]
    assert periodos_curva == sorted(periodos_curva)
    # La curva cubre al menos el rango de los períodos pedidos por el
    # usuario (T=500 en este fixture).
    assert periodos_curva[-1] >= max(_PERIODOS)
    assert all(p["valor"] is not None for p in curva)


@pytest.mark.integration
async def test_etapas_1_solo_no_pausa_en_etapa_2():
    """Con etapas=[1] el comportamiento debe ser exactamente el de antes
    de esta decisión — el criterio de hecho explícito del Bloque A."""
    gen, _ = _run_etapa2(etapas=[1])

    tipos_recibidos = [parse_sse(e)[0] async for e in gen]

    assert "result_etapa1" in tipos_recibidos
    assert "result_etapa2_ranking" not in tipos_recibidos
    assert "result_etapa2_eventos" not in tipos_recibidos
    assert tipos_recibidos[-1] == "complete"

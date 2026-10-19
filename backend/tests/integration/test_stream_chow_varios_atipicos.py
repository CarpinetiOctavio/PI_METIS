"""DECISIÓN 079 — Chow con varios atípicos en una sola pausa, una decisión por punto.

- `outlier_detected` trae todos los valores fuera de los umbrales, con su año.
- Rechazar dos y aceptar uno excluye exactamente los dos rechazados, juntos.
- Excluirlos con simulate-exclusion da el mismo resultado que rechazarlos en la
  pausa (la misma operación, DECISIÓN 071).
- Una decisión incompleta, con un índice ajeno o repetido no desbloquea nada.
"""

import numpy as np
import pytest

from metis.core.validacion.parser import parse_file
from metis.services import session_store
from metis.services.analysis_service import (
    DecisionAtipicoInvalidaError,
    registrar_outlier_decision,
    simular_exclusion,
)
from tests.integration._sse_helpers import parse_sse, run_stream

_BASE = list(np.random.default_rng(3).lognormal(4.6, 0.15, 37))
# Dos atípicos bajos (1985 y 2001) y uno alto (2019) — ver test_chow_todos_los_atipicos.py.
SERIE = _BASE[:5] + [3.0] + _BASE[5:20] + [2.0] + _BASE[20:] + [9000.0]
ANIOS = list(range(1980, 1980 + len(SERIE)))
GRUPOS = ("independencia", "homogeneidad", "tendencia", "atipicos")
CAMPOS = ("prueba", "estadistico", "valor_critico", "veredicto")


def _csv() -> bytes:
    filas = [f"{a},{v}" for a, v in zip(ANIOS, SERIE, strict=True)]
    return ("anio,caudal\n" + "\n".join(filas) + "\n").encode()


async def _correr(decidir) -> tuple[list[tuple[str, dict]], dict]:
    gen, session_id = run_stream(
        _csv(), columna_x="anio", tipo_variable="caudal_precipitacion"
    )
    eventos = []
    async for evento in gen:
        tipo, data = parse_sse(evento)
        eventos.append((tipo, data))
        if tipo == "outlier_detected":
            await registrar_outlier_decision(
                session_id=session_id, decisiones=decidir(data), db=None
            )
    final = next(d for t, d in eventos if t == "result_etapa1")
    return eventos, final


def _por_anio(data: dict, rechazar: set[int]) -> list[dict]:
    return [
        {
            "indice": a["indice"],
            "decision": "rechazar" if a["periodo"] in rechazar else "aceptar",
        }
        for a in data["atipicos"]
    ]


@pytest.mark.integration
async def test_la_pausa_presenta_los_tres_atipicos_con_su_anio_y_lado():
    eventos, _ = await _correr(lambda d: _por_anio(d, set()))

    pausas = [d for t, d in eventos if t == "outlier_detected"]
    assert len(pausas) == 1
    assert [(a["periodo"], a["lado"]) for a in pausas[0]["atipicos"]] == [
        (2019, "alto"),
        (2001, "bajo"),
        (1985, "bajo"),
    ]
    assert pausas[0]["valor_atipico"] == 9000.0  # compatibilidad


@pytest.mark.integration
async def test_dos_rechazos_y_una_aceptacion_excluyen_exactamente_los_dos():
    eventos, final = await _correr(lambda d: _por_anio(d, {1985, 2019}))

    anios = [t["anio"] for t in final["datos"]["timestamps_efectivos"]]
    assert 1985 not in anios and 2019 not in anios
    assert 2001 in anios
    assert len(final["datos"]["serie_efectiva"]) == len(SERIE) - 2
    assert 2.0 in final["datos"]["serie_efectiva"]
    # La segunda pasada informa Chow sin volver a pausar.
    assert sum(1 for t, _ in eventos if t == "outlier_detected") == 1


@pytest.mark.integration
async def test_excluir_k_puntos_por_simulacion_equivale_a_rechazarlos_en_la_pausa():
    _, final = await _correr(lambda d: _por_anio(d, {1985, 2019}))
    # La serie tal como la lee el stream del CSV (el texto redondea los floats).
    serie_leida = parse_file(_csv(), "serie.csv", "anio", "caudal").serie
    simulado = simular_exclusion(
        serie=serie_leida,
        anios=ANIOS,
        tipo_variable="caudal_precipitacion",
        cramer_particion="default",
        indices_excluidos=[ANIOS.index(1985), ANIOS.index(2019)],
        etapas=[1],
    )

    def resumen(e1: dict) -> list:
        return [{c: t[c] for c in CAMPOS} for g in GRUPOS for t in e1[g]]

    assert resumen(simulado["etapa1"]) == resumen(final)
    assert (
        simulado["etapa1"]["datos"]["serie_efectiva"]
        == final["datos"]["serie_efectiva"]
    )


@pytest.mark.integration
async def test_aceptar_todos_no_excluye_nada():
    _, final = await _correr(lambda d: _por_anio(d, set()))
    assert len(final["datos"]["serie_efectiva"]) == len(SERIE)


def _sesion_en_pausa(indices: list[int]) -> str:
    session_id = "sesion-chow"
    session_store.create_session(session_id)
    session_store.get_session(session_id).atipicos_pendientes = [
        {"indice": i} for i in indices
    ]
    return session_id


@pytest.mark.integration
@pytest.mark.parametrize(
    "decisiones",
    [
        [{"indice": 5, "decision": "rechazar"}],  # incompleta
        [
            {"indice": 5, "decision": "rechazar"},
            {"indice": 21, "decision": "aceptar"},
            {"indice": 7, "decision": "aceptar"},  # ajeno
        ],
        [
            {"indice": 5, "decision": "rechazar"},
            {"indice": 5, "decision": "aceptar"},  # repetido
        ],
        [],
    ],
    ids=["incompleta", "indice-ajeno", "repetido", "vacia"],
)
async def test_decision_que_no_cubre_exactamente_la_pausa_se_rechaza(decisiones):
    session_id = _sesion_en_pausa([5, 21])
    with pytest.raises(DecisionAtipicoInvalidaError):
        await registrar_outlier_decision(session_id, decisiones, db=None)
    assert not session_store.get_session(session_id).event.is_set()


@pytest.mark.integration
async def test_decision_sin_sesion_devuelve_none():
    assert (
        await registrar_outlier_decision(
            "no-existe", [{"indice": 0, "decision": "aceptar"}], db=None
        )
        is None
    )


def _csv_enmascarado() -> bytes:
    # Con el 90000 adentro, el 400 queda dentro de los umbrales; sin él, no.
    base = list(np.random.default_rng(3).lognormal(4.6, 0.15, 38))
    serie = base + [400.0, 90000.0]
    filas = [f"{1980 + i},{v}" for i, v in enumerate(serie)]
    return ("anio,caudal\n" + "\n".join(filas) + "\n").encode()


async def _final_enmascarado(decision: str) -> tuple[int, dict]:
    gen, session_id = run_stream(
        _csv_enmascarado(), columna_x="anio", tipo_variable="caudal_precipitacion"
    )
    pausas, final = 0, None
    async for evento in gen:
        tipo, data = parse_sse(evento)
        if tipo == "outlier_detected":
            pausas += 1
            await registrar_outlier_decision(
                session_id,
                [
                    {"indice": a["indice"], "decision": decision}
                    for a in data["atipicos"]
                ],
                db=None,
            )
        elif tipo == "result_etapa1":
            final = data
    return pausas, final


def _warning_chow(final: dict) -> str:
    return next(
        w["descripcion"]
        for w in final["warnings"]
        if w["codigo"] == "TEST_WARNING_OUTLIER_DETECTED"
    )


@pytest.mark.integration
async def test_segunda_pasada_con_atipicos_nuevos_los_informa_sin_volver_a_pausar():
    pausas, final = await _final_enmascarado("rechazar")

    assert pausas == 1
    chow = next(t for t in final["atipicos"] if t["prueba"] == "chow")
    assert [a["valor"] for a in chow["valores_atipicos"]] == [400.0]
    assert "valor(es) nuevo(s)" in _warning_chow(final)
    assert "2018" in _warning_chow(final)
    assert "pendiente" not in _warning_chow(final)


@pytest.mark.integration
async def test_aceptar_todos_deja_de_decir_decision_pendiente():
    _, final = await _final_enmascarado("aceptar")
    assert "aceptaste" in _warning_chow(final)
    assert "2019" in _warning_chow(final)

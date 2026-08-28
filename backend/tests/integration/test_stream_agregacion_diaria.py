"""
docs/plan-resolucion-diaria.md (R2-R3) — integración de punta a punta:
una serie DIARIA subida vía stream_analysis() se agrega a máximos anuales
antes de correr Etapa 1 (espejo de test_stream_agregacion_mensual.py).

Cubre los dos casos que R5 marca como fáciles de volver a romper:
  1. Rechazar el atípico de Chow sobre la serie diaria agregada mapea el
     índice contra serie_efectiva (n≈15), no contra la serie diaria cruda
     (n≈5500).
  2. serie_calendario se calcula por el camino DIRECTO diaria -> anual
     (R3.4): sin `resolucion=` explícito, la segunda agregación correría en
     modo "mensual" sobre datos diarios y devolvería el máximo de los
     últimos días de cada mes — silencioso y equivocado.
"""

import json
import uuid

import pandas as pd
import pytest

from metis.services import session_store
from metis.services.analysis_service import (
    registrar_outlier_decision,
    stream_analysis,
)


def _csv_diario(
    anio_inicio: int,
    anios: int,
    *,
    anio_pico: int | None = None,
    valor_pico: float = 5000.0,
) -> bytes:
    """Serie diaria: base 10.0 todos los días, salvo un pico el 15 de julio
    de cada año (100 + offset del año) — así el máximo anual real NUNCA es
    el valor del último día de un mes. Opcionalmente un año con un pico
    gigante para forzar un atípico de Chow sobre la serie agregada.
    """
    inicio = pd.Timestamp(year=anio_inicio, month=1, day=1)
    fin = pd.Timestamp(year=anio_inicio + anios - 1, month=12, day=31)
    filas = ["fecha,caudal"]
    for d in pd.date_range(inicio, fin, freq="D"):
        valor = 10.0
        if d.month == 7 and d.day == 15:
            valor = 100.0 + (d.year - anio_inicio)
            if anio_pico is not None and d.year == anio_pico:
                valor = valor_pico
        filas.append(f"{d.strftime('%Y-%m-%d')},{valor:.4f}")
    return ("\n".join(filas) + "\n").encode()


def _parse_sse(evento: str) -> tuple[str, dict]:
    lineas = evento.strip("\n").split("\n")
    tipo = lineas[0].removeprefix("event: ")
    data = json.loads(lineas[1].removeprefix("data: "))
    return tipo, data


@pytest.fixture(autouse=True)
def _limpiar_sessions():
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


@pytest.mark.integration
async def test_serie_diaria_se_agrega_y_termina_en_15_anios():
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_diario(2000, 15),
        filename="serie.csv",
        columna_x="fecha",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1],
        session_id=session_id,
        user_id=None,
        db=None,
        mes_inicio_anio=1,
    )

    payload_result = None
    async for evento_crudo in gen:
        tipo, data = _parse_sse(evento_crudo)
        if tipo == "result_etapa1":
            payload_result = data

    assert payload_result is not None
    assert payload_result["contract"]["bloqueante"] is False
    assert payload_result["descriptive"]["n"] == 15
    datos = payload_result["datos"]
    assert datos["resolucion_original"] == "diaria"
    # R3.3 opción 2 — el payload lleva la agregación MENSUAL, no la diaria cruda.
    assert datos["resolucion_serie_original"] == "mensual"
    assert len(datos["serie_original"]) == 15 * 12
    assert len(datos["timestamps_originales"]) == 15 * 12
    # serie_efectiva son los 15 máximos anuales.
    assert len(datos["serie_efectiva"]) == 15
    # El máximo anual real es el pico del 15 de julio (100 + offset), nunca
    # el 10.0 de los días de fin de mes.
    assert min(datos["serie_efectiva"]) >= 100.0


@pytest.mark.integration
async def test_rechazar_atipico_sobre_serie_diaria_agregada_no_rompe_el_indice():
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_diario(2000, 15, anio_pico=2007),
        filename="serie.csv",
        columna_x="fecha",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1],
        session_id=session_id,
        user_id=None,
        db=None,
        mes_inicio_anio=1,
    )

    tipos_recibidos: list[str] = []
    valor_atipico = None
    payload_final = None

    async for evento_crudo in gen:
        tipo, data = _parse_sse(evento_crudo)
        tipos_recibidos.append(tipo)
        if tipo == "outlier_detected":
            valor_atipico = data["valor_atipico"]
            await registrar_outlier_decision(
                session_id=session_id,
                decision="rechazar",
                dato_atipico=valor_atipico,
                db=None,
            )
        elif tipo == "result_etapa1":
            payload_final = data

    assert "outlier_detected" in tipos_recibidos
    # El atípico es el máximo anual agregado de 2007 (~5000), nunca un valor
    # diario crudo (10 o ~100).
    assert valor_atipico == pytest.approx(5000.0, rel=1e-3)

    assert payload_final is not None
    assert payload_final["descriptive"]["n"] == 14  # 15 años menos 2007
    assert payload_final["descriptive"]["maximo"] < 1000.0

    datos = payload_final["datos"]
    assert datos["resolucion_original"] == "diaria"
    assert datos["resolucion_serie_original"] == "mensual"
    # serie_original del resultado final sigue siendo la agregación mensual
    # de TODA la subida (180 meses), no la diaria cruda ni la recortada.
    assert len(datos["serie_original"]) == 15 * 12
    assert len(datos["serie_efectiva"]) == 14
    assert len(datos["timestamps_efectivos"]) == 14
    assert datos["indice_atipico"] is None
    anios_efectivos = [t["anio"] for t in datos["timestamps_efectivos"]]
    assert anios_efectivos == [a for a in range(2000, 2015) if a != 2007]


@pytest.mark.integration
async def test_serie_calendario_diaria_por_camino_directo():
    # mes_inicio_anio=7 (no calendario) + carga diaria -> serie_calendario se
    # calcula recomponiendo con mes_inicio=1 SOBRE LA SERIE DIARIA CRUDA
    # (R3.4). El valor de cada año calendario tiene que ser el máximo de los
    # valores DIARIOS de ese año (el pico del 15 de julio), no el máximo de
    # los máximos mensuales por un camino encadenado, y sobre todo no el
    # 10.0 de los últimos días de mes que devolvería la llamada sin
    # `resolucion=`.
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_diario(2000, 15),
        filename="serie.csv",
        columna_x="fecha",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1],
        session_id=session_id,
        user_id=None,
        db=None,
        mes_inicio_anio=7,
    )

    payload_result = None
    async for evento_crudo in gen:
        tipo, data = _parse_sse(evento_crudo)
        if tipo == "result_etapa1":
            payload_result = data

    assert payload_result is not None
    serie_cal = payload_result["datos"]["serie_calendario"]
    assert serie_cal is not None
    # Años calendario completos: 2000..2014 (el pico de julio los hace
    # completos por sí solos solo si el año entero está — mes_inicio=1).
    valores = serie_cal["serie"]
    anios = [t["anio"] for t in serie_cal["timestamps"]]
    # Para cada año calendario presente, el valor es el pico de julio de ese
    # año (100 + offset), NUNCA 10.0.
    for anio, valor in zip(anios, valores):
        assert valor == pytest.approx(100.0 + (anio - 2000)), f"año {anio}"

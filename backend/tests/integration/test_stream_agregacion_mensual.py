"""
Bloque F3-F4 del plan de implementación de Etapa 2 (DECISIÓN 057) —
integración de punta a punta: una serie MENSUAL subida vía stream_analysis()
se agrega a máximos anuales antes de correr Etapa 1, y — el bug real que
motivó agregar serie_efectiva/timestamps_efectivos a Etapa1Result — el
mapeo de índice de Chow sigue funcionando cuando el usuario rechaza un
atípico sobre la serie YA agregada, no sobre los valores mensuales crudos.

Antes de este fix, _mapear_indice_a_serie_original() se llamaba con
serie_original (mensual, ~180 elementos) usando un índice calculado sobre
la serie anual agregada (~15 elementos) — habría borrado un dato mensual
en una posición sin relación con el atípico real.
"""

import json
import uuid

import numpy as np
import pytest

from metis.services import session_store
from metis.services.analysis_service import (
    registrar_outlier_decision,
    stream_analysis,
)

_rng = np.random.default_rng(seed=3)


def _csv_mensual_con_atipico() -> bytes:
    """15 años de datos mensuales (ene2000-dic2014), valores moderados
    salvo un único mes de 2007 con un valor mucho más grande — garantiza
    que el máximo anual agregado de 2007 sea un atípico real para Chow."""
    filas = ["fecha,caudal"]
    anio, mes = 2000, 1
    for i in range(15 * 12):
        valor = _rng.uniform(50, 100)
        if anio == 2007 and mes == 6:
            valor = 5000.0  # atípico garantizado para el año agregado 2007
        filas.append(f"{anio:04d}-{mes:02d}-01,{valor:.4f}")
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
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
async def test_serie_mensual_se_agrega_y_termina_en_15_anios_sin_atipico_previo():
    # etapas=[1] solamente, mes_inicio_anio=1 (calendario) — sin el pico de
    # 2007, para aislar primero que la agregación en sí funciona de punta a
    # punta antes de mezclar con el flujo de Chow.
    session_id = str(uuid.uuid4())
    filas = ["fecha,caudal"]
    anio, mes = 2000, 1
    for _ in range(15 * 12):
        filas.append(f"{anio:04d}-{mes:02d}-01,{_rng.uniform(50, 100):.4f}")
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
    csv = ("\n".join(filas) + "\n").encode()

    gen = stream_analysis(
        content=csv,
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


@pytest.mark.integration
async def test_rechazar_atipico_sobre_serie_mensual_agregada_no_rompe_el_indice():
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_mensual_con_atipico(),
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
    # El atípico detectado tiene que ser el máximo anual de 2007 (~5000),
    # nunca uno de los valores mensuales crudos (50-100).
    assert valor_atipico == pytest.approx(5000.0, rel=1e-3)

    assert payload_final is not None
    assert payload_final["contract"]["bloqueante"] is False
    # 15 años agregados, menos el año 2007 (el atípico rechazado) = 14.
    # Si el mapeo de índice estuviera roto, esto fallaría (n distinto de
    # 14, o el atípico seguiría presente tras "rechazar").
    assert payload_final["descriptive"]["n"] == 14
    assert payload_final["descriptive"]["maximo"] < 1000.0

    # PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058) — el
    # bloque "datos" del resultado FINAL (la segunda ejecución de
    # ejecutar_etapa1(), sobre la serie ya sin el atípico) tiene que seguir
    # exponiendo la serie mensual cruda ORIGINAL, no la que vio esa segunda
    # ejecución (que ya no tiene acceso a los datos mensuales — corre sobre
    # serie_efectiva menos un punto). Sin el copiado explícito de
    # serie_original/timestamps_originales desde la primera ejecución en
    # stream_analysis(), este bloque quedaría con resolucion_original
    # forzado a "anual" y sin la serie mensual — exactamente el hueco que
    # bloqueaba el boxplot mensual (FE-16).
    datos = payload_final["datos"]
    assert datos["resolucion_original"] == "mensual"
    assert datos["serie_original"] is not None
    assert len(datos["serie_original"]) == 15 * 12  # los 180 meses crudos
    assert len(datos["timestamps_originales"]) == 15 * 12
    # serie_efectiva del resultado final: 14 años (post-rechazo), no 15.
    assert len(datos["serie_efectiva"]) == 14
    # No quedó ningún atípico nuevo tras rechazar el primero.
    assert datos["indice_atipico"] is None
    # mes_inicio_anio=1 en este test — la calendario ya ES la efectiva.
    assert datos["serie_calendario"] is None

    # Hallazgo V2 (plan post-avance, 14/08/2026): timestamps_efectivos tenía
    # un elemento más que serie_efectiva tras rechazar, porque se filtraba
    # solo la serie y no los timestamps con el mismo índice — todo punto
    # posterior al atípico quedaba corrido un año en los gráficos de la
    # serie temporal y de Chow. Sin el fix, esto falla con 15 != 14.
    assert len(datos["timestamps_efectivos"]) == len(datos["serie_efectiva"]) == 14
    # El año 2007 (el atípico rechazado) no debe aparecer, y no debe haber
    # ningún año duplicado ni faltante aparte de 2007 — si el índice
    # filtrado no correspondiera al mismo elemento en ambas listas, algún
    # otro año terminaría faltando o duplicado en su lugar.
    anios_efectivos = [t["anio"] for t in datos["timestamps_efectivos"]]
    assert anios_efectivos == [a for a in range(2000, 2015) if a != 2007]

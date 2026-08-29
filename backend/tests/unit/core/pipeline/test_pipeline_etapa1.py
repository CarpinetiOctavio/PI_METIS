import numpy as np
import pandas as pd
import pytest

from metis.core.pipeline import ejecutar_etapa1


def _fechas_mensuales(anio_inicio: int, mes_inicio: int, cantidad: int) -> list[str]:
    fechas = []
    anio, mes = anio_inicio, mes_inicio
    for _ in range(cantidad):
        fechas.append(f"{anio:04d}-{mes:02d}-01")
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
    return fechas


def _fechas_diarias(inicio: str, fin: str) -> list[str]:
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(inicio, fin, freq="D")]


# Serie que produce nivel_confianza="validado" — todas las pruebas aprueban.
# numpy seed=9, uniform(10, 100), n=50. Seed 1 fue descartada (Helmert rechaza
# con criterio directo |S-C| ≤ √(n-1): margen=0). Seed 9: margen=6 (holgado).
# n=50 > 40 evita TEST_WARNING_SMALL_SAMPLE de Wald-Wolfowitz.
# Verificada con smoke test antes de incorporar como constante.
_rng = np.random.default_rng(seed=9)
SERIE_VALIDADA = _rng.uniform(10, 100, size=50).tolist()


# ── Pipeline bloqueante ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_serie_bloqueante_detiene_pipeline():
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.descriptive is None
    assert resultado.independencia == []
    assert resultado.homogeneidad == []
    assert resultado.tendencia == []
    assert resultado.atipicos == []


@pytest.mark.unit
def test_sin_resolucion_temporal_detiene_pipeline():
    serie = [float(i) for i in range(10, 20)]
    resultado = ejecutar_etapa1(serie, "otro", resolucion_temporal=None)
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.independencia == []
    assert resultado.homogeneidad == []
    assert resultado.tendencia == []
    assert resultado.atipicos == []


@pytest.mark.unit
def test_strings_con_menos_de_10_numericos_bloqueante():
    # 5 floats + 5 strings — el filtrado ocurre antes de validar el mínimo de 10.
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, "a", "b", "c", "d", "e"]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.independencia == []


# ── Bloque H3 (plan post-avance, DECISIÓN 030) — orden cronológico ────────────
# Tests que separan explícitamente "desorden bloquea" de "datos faltantes NO
# bloquean" — son dos cosas distintas, la decisión original insiste en no
# mezclarlas (ver docs/decisiones/decision030.md).


@pytest.mark.unit
def test_timestamps_desordenados_bloquea_serie_anual():
    serie = [float(i) for i in range(30)]
    timestamps = list(range(1980, 2010))
    timestamps[5], timestamps[6] = timestamps[6], timestamps[5]  # swap dos años

    resultado = ejecutar_etapa1(serie, "otro", "anual", timestamps=timestamps)

    assert resultado.contract.bloqueante is True
    assert resultado.contract.codigo_error == "CONTRACT_WRONG_ORDER"
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.independencia == []


@pytest.mark.unit
def test_timestamps_en_orden_con_datos_faltantes_no_bloquea():
    # Distinción explícita: un dato faltante (None) NO es desorden — sigue
    # su tratamiento actual (CONTRACT_MISSING_VALUES, warning normal), sin
    # que el chequeo nuevo de orden lo confunda con el caso bloqueante.
    serie = [float(i) for i in range(29)] + [None]
    timestamps = list(range(1980, 2010))

    resultado = ejecutar_etapa1(serie, "otro", "anual", timestamps=timestamps)

    assert resultado.contract.bloqueante is False
    assert resultado.nivel_confianza != "rechazado"
    codigos = [w.codigo for w in resultado.warnings]
    assert "CONTRACT_MISSING_VALUES" in codigos
    assert "CONTRACT_WRONG_ORDER" not in codigos


@pytest.mark.unit
def test_sin_timestamps_el_chequeo_de_orden_no_se_evalua():
    # timestamps=None (CU-03 sin columna de fecha, por ejemplo) — nada que
    # ordenar, el pipeline sigue corriendo normalmente en vez de fallar
    # por intentar comparar None.
    resultado = ejecutar_etapa1(SERIE_VALIDADA, "otro", "anual", timestamps=None)
    assert resultado.contract.bloqueante is False
    assert resultado.nivel_confianza == "validado"


@pytest.mark.unit
def test_bug_agregacion_mensual_desordenada_pierde_periodos_en_silencio_antes_bloquea_ahora():
    # El segundo problema, más grave, que la DECISIÓN 030 original no
    # contemplaba: agregar_a_maximos_anuales() toma timestamps[0]/[-1]
    # como si fueran el dato más antiguo/reciente del registro para fijar
    # el rango de períodos a agregar. Verificado ANTES de este fix, contra
    # el código sin parchear: con 3 años completos (36 meses reales)
    # desordenados así (2000, 2002, 2001 — dos bloques anuales
    # invertidos), agregar_a_maximos_anuales() devolvía serie=[año 2000,
    # año 2001] con periodos_descartados=[] — el año 2002 completo
    # desaparecía sin ningún rastro, ni warning ni error. Con el chequeo
    # de orden ANTES del paso 0, este archivo bloquea antes de llegar
    # siquiera a agregar_a_maximos_anuales() — la pérdida silenciosa deja
    # de ser posible por construcción, no por casualidad.
    timestamps = (
        _fechas_mensuales(2000, 1, 12)
        + _fechas_mensuales(2002, 1, 12)
        + _fechas_mensuales(2001, 1, 12)
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="mensual",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is True
    assert resultado.contract.codigo_error == "CONTRACT_WRONG_ORDER"
    assert resultado.nivel_confianza == "rechazado"


# ── Pipeline completo ─────────────────────────────────────────────────────────


@pytest.mark.unit
def test_serie_valida_nivel_confianza_validado():
    # SERIE_VALIDADA: numpy seed=1, n=50 — todas las pruebas aprueban sin warnings.
    # serie_facundo no sirve para este caso: Anderson rechaza (dependiente).
    resultado = ejecutar_etapa1(SERIE_VALIDADA, "otro", "anual")
    assert resultado.nivel_confianza == "validado"
    assert resultado.independencia[0].prueba == "anderson"
    assert resultado.independencia[0].veredicto == "aprobada"
    assert resultado.homogeneidad[0].prueba == "helmert"
    assert resultado.homogeneidad[0].veredicto == "aprobada"
    assert resultado.tendencia[0].prueba == "mann_kendall"
    assert resultado.tendencia[0].veredicto == "aprobada"
    assert resultado.atipicos[0].prueba == "chow"
    assert resultado.atipicos[0].veredicto == "aprobada"
    assert resultado.descriptive is not None


@pytest.mark.unit
def test_warning_critico_produce_con_warnings(serie_facundo):
    # serie_facundo: Wald n=40 ≤ 40 → TEST_WARNING_SMALL_SAMPLE → con_warnings.
    resultado = ejecutar_etapa1(serie_facundo, "caudal_precipitacion", "anual")
    assert resultado.nivel_confianza == "con_warnings"


# ── Comportamientos específicos ───────────────────────────────────────────────


@pytest.mark.unit
def test_ceros_en_caudal_chow_no_ejecutada_pipeline_continua():
    # Ceros en caudal_precipitacion → Chow no ejecutada, pero el pipeline continúa.
    serie = [0.0, 5.0] + [float(i) for i in range(10, 59)]
    resultado = ejecutar_etapa1(serie, "caudal_precipitacion", "anual")
    assert resultado.nivel_confianza == "con_warnings"
    assert len(resultado.atipicos) == 1
    assert resultado.atipicos[0].veredicto == "no_ejecutada"
    assert resultado.atipicos[0].warning_codigo == "TEST_NOT_EXECUTED_ZEROS"


@pytest.mark.unit
def test_strings_filtrados_antes_de_pruebas():
    # 30 floats + strings mezclados — pruebas reciben solo los numéricos.
    serie = [float(i) for i in range(10, 40)] + ["x", "y", "z"]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    codigos = [w.codigo for w in resultado.warnings]
    assert "CONTRACT_NON_NUMERIC_VALUES" in codigos
    assert resultado.independencia[0].prueba == "anderson"
    assert resultado.independencia[0].estadistico is not None
    assert resultado.homogeneidad[0].prueba == "helmert"
    assert resultado.homogeneidad[0].estadistico is not None


@pytest.mark.unit
def test_cramer_siempre_incluye_n1_y_n2(serie_facundo):
    resultado = ejecutar_etapa1(serie_facundo, "caudal_precipitacion", "anual")
    cramer = next(t for t in resultado.homogeneidad if t.prueba == "cramer")
    assert cramer.n1 is not None
    assert cramer.n2 is not None
    assert cramer.n1 > 0
    assert cramer.n2 > 0


@pytest.mark.unit
def test_t_student_usa_particion_mitad_mitad_no_particion_cramer():
    # Regresión de cableado: t-Student exige n1=n2=n/2 (III-8), independiente
    # de la partición 60%/30% que usa Cramer (cramer_particion). Antes del fix,
    # pipeline.py reutilizaba por error la partición de Cramer (n1=14, n2=7
    # para esta serie) como argumento de calcular_t_student.
    # Serie real est_02 (Vado de Río Seco — Río Barrancas, n=24), tesis Facundo:
    # t esperado=-1.76, GL=22, valor_critico=2.0739, veredicto="aprobada".
    serie_est02 = [
        98.0,
        44.0,
        97.0,
        52.0,
        90.0,
        247.0,
        191.0,
        54.0,
        112.0,
        42.0,
        60.0,
        157.0,
        61.0,
        45.0,
        91.0,
        257.0,
        458.0,
        381.0,
        251.0,
        151.0,
        122.0,
        58.0,
        145.0,
        158.0,
    ]
    resultado = ejecutar_etapa1(serie_est02, "otro", "anual")
    t_student = next(t for t in resultado.homogeneidad if t.prueba == "t_student")

    assert t_student.n1 == 12
    assert t_student.n2 == 12
    assert t_student.estadistico == pytest.approx(-1.7643, abs=1e-3)
    assert t_student.valor_critico == pytest.approx(2.0739, abs=1e-3)
    assert t_student.veredicto == "aprobada"


# ── Agregación temporal (Bloque F4) ───────────────────────────────────────────


@pytest.mark.unit
def test_resolucion_anual_serie_efectiva_es_la_serie_de_entrada():
    # Sin agregación (resolucion_temporal="anual"), serie_efectiva /
    # timestamps_efectivos tienen que reflejar exactamente lo que entró —
    # comportamiento idéntico al de antes del Bloque F4.
    resultado = ejecutar_etapa1(SERIE_VALIDADA, "otro", "anual")
    assert resultado.serie_efectiva == SERIE_VALIDADA


@pytest.mark.unit
def test_serie_mensual_con_anios_completos_se_agrega_antes_de_las_pruebas():
    # F2.1 — 12 años completos (144 meses) mensuales, mes_inicio=1: el
    # pipeline tiene que correr sobre los 12 máximos anuales, no sobre los
    # 144 valores mensuales crudos.
    timestamps = _fechas_mensuales(2000, 1, 144)
    serie = [float(i % 12) + (i // 12) for i in range(144)]  # valores variados

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="mensual",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is False
    assert len(resultado.serie_efectiva) == 12
    assert resultado.timestamps_efectivos == list(range(2000, 2012))


@pytest.mark.unit
def test_serie_mensual_con_recorte_emite_warning_partial_years_trimmed():
    # 11 años completos + 3 meses sueltos al final (año 12 incompleto,
    # mes_inicio=1) -> se recorta, con warning no bloqueante.
    timestamps = _fechas_mensuales(2000, 1, 11 * 12 + 3)
    serie = [float(i) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="mensual",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is False
    assert len(resultado.serie_efectiva) == 11
    codigos = [w.codigo for w in resultado.warnings]
    assert "CONTRACT_PARTIAL_YEARS_TRIMMED" in codigos


@pytest.mark.unit
def test_carga_diaria_emite_daily_series_aggregated_informativo_por_default():
    # PR 2.5 (R0.2) — con carga diaria y variable_diaria por default ("pico"),
    # se emite CONTRACT_DAILY_SERIES_AGGREGATED con texto informativo, sin
    # advertencia de sesgo.
    timestamps = _fechas_diarias("2000-01-01", "2011-12-31")  # 12 años calendario
    serie = [float(i % 37) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="diaria",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is False
    assert len(resultado.serie_efectiva) == 12
    daily = next(
        w for w in resultado.warnings if w.codigo == "CONTRACT_DAILY_SERIES_AGGREGATED"
    )
    assert daily.nivel == "normal"
    assert "picos o máximos diarios" in daily.descripcion
    assert "subestimar" not in daily.descripcion


@pytest.mark.unit
def test_carga_diaria_media_advierte_sesgo_a_la_baja():
    # variable_diaria="media" -> el mismo código, texto que advierte que los
    # máximos anuales y los eventos de diseño subestiman el pico instantáneo.
    timestamps = _fechas_diarias("2000-01-01", "2011-12-31")
    serie = [float(i % 37) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="diaria",
        timestamps=timestamps,
        mes_inicio_anio=1,
        variable_diaria="media",
    )

    daily = next(
        w for w in resultado.warnings if w.codigo == "CONTRACT_DAILY_SERIES_AGGREGATED"
    )
    assert "MEDIAS diarias" in daily.descripcion
    assert "subestimar el pico instantáneo real" in daily.descripcion


@pytest.mark.unit
def test_carga_mensual_no_emite_daily_series_aggregated():
    timestamps = _fechas_mensuales(2000, 1, 12 * 12)
    serie = [float(i) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="mensual",
        timestamps=timestamps,
        mes_inicio_anio=1,
        variable_diaria="media",  # se pasa igual, pero la serie no es diaria
    )

    codigos = [w.codigo for w in resultado.warnings]
    assert "CONTRACT_DAILY_SERIES_AGGREGATED" not in codigos


@pytest.mark.unit
def test_recorte_mensual_que_deja_n_menor_a_10_es_bloqueante():
    # F7 — el recorte ocurre ANTES del conteo de la regla de n: 8 años
    # completos agregados (n=8 < 10) tienen que bloquear con
    # CONTRACT_SERIES_TOO_SHORT, igual que cualquier otra serie corta.
    timestamps = _fechas_mensuales(2000, 1, 8 * 12)
    serie = [float(i) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="mensual",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is True
    assert resultado.contract.codigo_error == "CONTRACT_SERIES_TOO_SHORT"
    assert resultado.nivel_confianza == "rechazado"


@pytest.mark.unit
def test_carga_diaria_el_recorte_deja_n_menor_a_10_y_bloquea():
    # R5 (docs/plan-resolucion-diaria.md) — espejo diario del test mensual de
    # recorte: el conteo de la regla de n opera sobre la serie YA agregada,
    # así que un registro que pierde años por recorte de extremos puede
    # quedar bajo el piso y bloquear como cualquier serie corta. No es una
    # excepción nueva del camino diario, es la regla existente aplicada
    # después del paso 0.
    #
    # 2000-04-01 → 2010-09-30 con mes_inicio_anio=1: 2000 y 2010 son años
    # parciales (se recortan) y quedan 2001..2009 = 9 años completos < 10.
    timestamps = _fechas_diarias("2000-04-01", "2010-09-30")
    serie = [float(i % 53) for i in range(len(timestamps))]

    resultado = ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal="diaria",
        timestamps=timestamps,
        mes_inicio_anio=1,
    )

    assert resultado.contract.bloqueante is True
    assert resultado.contract.codigo_error == "CONTRACT_SERIES_TOO_SHORT"
    assert resultado.nivel_confianza == "rechazado"
    # el recorte se reporta igual, aunque el pipeline se haya detenido
    assert "CONTRACT_PARTIAL_YEARS_TRIMMED" in [w.codigo for w in resultado.warnings]

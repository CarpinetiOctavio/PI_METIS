import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from metis.core.etapa1.outliers import calcular_chow
from metis.core.pipeline import ejecutar_etapa1
from metis.core.types import ContractResult, Etapa1Result, TestResult
from metis.services.analysis_service import (
    _extraer_atipico,
    _extraer_indice_atipico,
    _mapear_indice_a_serie_original,
    _persistir,
)


def _etapa1_result_con_chow(chow: TestResult) -> Etapa1Result:
    """Construye un Etapa1Result mínimo con un único TestResult de Chow,
    para testear _extraer_atipico/_extraer_indice_atipico de forma aislada,
    sin correr el pipeline completo."""
    return Etapa1Result(
        contract=ContractResult(bloqueante=False, codigo_error=None),
        descriptive=None,
        independencia=[],
        homogeneidad=[],
        tendencia=[],
        atipicos=[chow],
        nivel_independencia=None,
        nivel_homogeneidad=None,
        nivel_confianza="con_warnings",
    )


# ── Fix 2 — indice_atipico se propaga desde calcular_chow() ────────────────


@pytest.mark.unit
def test_extraer_indice_atipico_lee_el_indice_real_de_chow():
    # Atípico evidente en la posición 20 (500.0 entre valores ~10).
    serie = [10.0] * 20 + [500.0]
    chow = calcular_chow(serie, "otro")
    assert chow.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED"
    assert chow.indice_atipico == 20
    assert chow.valor_atipico == 500.0

    result = _etapa1_result_con_chow(chow)
    assert _extraer_atipico(result) == 500.0
    assert _extraer_indice_atipico(result) == 20


@pytest.mark.unit
def test_extraer_indice_atipico_none_si_no_hay_atipico():
    # Serie homogénea, sin atípico — Chow aprueba.
    serie = [10.0, 10.5, 9.8, 10.2, 9.9, 10.1, 10.3, 9.7, 10.0, 10.4, 9.6]
    chow = calcular_chow(serie, "otro")
    assert chow.veredicto == "aprobada"

    result = _etapa1_result_con_chow(chow)
    assert _extraer_atipico(result) is None
    assert _extraer_indice_atipico(result) is None


# ── Fix 3 — remoción por índice, no por valor ───────────────────────────────


@pytest.mark.unit
def test_remocion_por_indice_no_por_valor_con_duplicado():
    """
    Regresión del bug de analysis_service.py: serie_filtrada.remove(valor_atipico)
    borra por VALOR (primer match de la lista), no por posición. Si el valor que
    Chow marcó como atípico coincide, por coincidencia numérica, con un dato
    legítimo en otra posición de la serie, remove(valor) puede borrar el dato
    equivocado si ese dato legítimo aparece antes en la lista.

    NOTA METODOLÓGICA: calcular_chow() resuelve empates de z-score máximo con
    np.argmax(), que siempre devuelve la PRIMERA ocurrencia del máximo — el
    mismo criterio de desempate que list.remove(). Por eso, si el valor
    atípico real está literalmente duplicado en la serie, ambas estrategias
    (por índice y por valor) coinciden hoy en la práctica; no hay forma de
    reproducir la divergencia generando la serie y dejando que calcular_chow()
    la resuelva "naturalmente" — se verificó esto de forma numérica antes de
    escribir el test.

    Este test no depende de ese detalle de implementación de calcular_chow().
    Ataca directamente el contrato que sí importa para stream_analysis(): dado
    un TestResult de Chow con indice_atipico=K, la remoción debe sacar
    exactamente la posición K de la serie — sin importar si arr[K] coincide
    con el valor de otra posición legítima anterior. Se construye el
    TestResult a mano para fijar esa condición explícitamente, en vez de
    depender de que el generador de datos la produzca por accidente.
    """
    # Posición 0 = dato legítimo (10.0). Posición 5 = atípico real, cuyo
    # valor (10.0) coincide "por accidente" con el dato legítimo de la
    # posición 0 — mismo valor, dos posiciones distintas y con distinto
    # significado dentro de la serie.
    serie_original = [10.0, 500.0, 501.0, 499.5, 500.2, 10.0, 500.1, 499.8]
    indice_atipico_real = 5  # el que "Chow" reporta para este caso

    chow = TestResult(
        prueba="chow",
        estadistico=99.0,
        valor_critico=2.5,
        veredicto="rechazada",
        warning_codigo="TEST_WARNING_OUTLIER_DETECTED",
        warning_nivel="normal",
        valor_atipico=serie_original[indice_atipico_real],
        indice_atipico=indice_atipico_real,
    )
    result = _etapa1_result_con_chow(chow)

    indice = _extraer_indice_atipico(result)
    assert indice == indice_atipico_real

    # Fix aplicado: remoción posicional.
    serie_correcta = serie_original.copy()
    del serie_correcta[indice]
    assert serie_correcta == [10.0, 500.0, 501.0, 499.5, 500.2, 500.1, 499.8]
    # El dato legítimo de la posición 0 sigue presente.
    assert serie_correcta[0] == 10.0
    assert len(serie_correcta) == len(serie_original) - 1

    # Bug que reemplaza: remoción por valor habría borrado la posición 0
    # (primer match de 10.0), no la posición 5 que señaló Chow.
    valor_atipico = _extraer_atipico(result)
    serie_bug = serie_original.copy()
    serie_bug.remove(valor_atipico)
    assert serie_bug == [500.0, 501.0, 499.5, 500.2, 10.0, 500.1, 499.8]
    assert serie_bug != serie_correcta
    # Con el bug viejo se borró el dato legítimo de la posición 0 (10.0),
    # no la posición 5 que señaló Chow — el atípico real sigue en la serie.
    assert serie_bug[0] == 500.0
    assert 10.0 in serie_bug


# ── Fix 3 (continuación) — mapeo de índice cuando hay valores faltantes ────


@pytest.mark.unit
def test_remocion_mapea_indice_cuando_hay_valor_faltante_antes_del_atipico():
    """
    Regresión: indice_atipico que devuelve calcular_chow() está calculado
    sobre valores_numericos — la serie ya filtrada dentro de
    ejecutar_etapa1() vía filtrar_numericos() — no sobre serie_original.
    Si hay algún valor faltante (None) en una posición anterior a la del
    atípico, el índice queda desalineado: sin el mapeo, se borra el vecino
    equivocado de serie_original, sin ninguna coincidencia de valores de
    por medio — solo por el corrimiento de posiciones entre las dos listas.

    Reproduce el caso reportado: None en la posición 3 de serie_original,
    atípico real (500.0) en la posición 21 de serie_original — pero en el
    espacio filtrado (sin el None) esa misma posición pasa a ser la 20,
    que es lo que calcular_chow() efectivamente reporta.
    """
    serie_original = [10.0, 10.0, 10.0, None] + [10.0] * 17 + [500.0]
    timestamps = list(range(1980, 1980 + len(serie_original)))

    resultado = ejecutar_etapa1(serie_original, "otro", "anual", timestamps=timestamps)
    chow = next(t for t in resultado.atipicos if t.prueba == "chow")
    assert chow.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED"
    assert chow.valor_atipico == 500.0

    result = _etapa1_result_con_chow(chow)
    indice_filtrado = _extraer_indice_atipico(result)
    # Índice en valores_numericos (21 elementos, sin el None) — NO coincide
    # con la posición real de 500.0 en serie_original (22 elementos).
    assert indice_filtrado == 20
    assert serie_original[indice_filtrado] == 10.0  # el vecino, no el atípico
    assert serie_original[indice_filtrado] != chow.valor_atipico

    # Con el mapeo: la posición real en serie_original es 21.
    indice_real = _mapear_indice_a_serie_original(indice_filtrado, serie_original)
    assert indice_real == 21
    assert serie_original[indice_real] == chow.valor_atipico == 500.0

    serie_filtrada = serie_original.copy()
    del serie_filtrada[indice_real]

    assert 500.0 not in serie_filtrada
    assert serie_filtrada.count(10.0) == 20  # los 20 legítimos, todos presentes
    assert serie_filtrada[3] is None  # el None no lo toca este fix, sigue ahí
    assert len(serie_filtrada) == len(serie_original) - 1


# ── F7a (plan de fixes pre-reunión) — nombre_archivo en configuracion ──────


def _etapa1_result_minimo() -> Etapa1Result:
    return Etapa1Result(
        contract=ContractResult(bloqueante=False, codigo_error=None),
        descriptive=None,
        independencia=[],
        homogeneidad=[],
        tendencia=[],
        atipicos=[],
        nivel_independencia=None,
        nivel_homogeneidad=None,
        nivel_confianza="validado",
    )


@pytest.mark.unit
async def test_persistir_guarda_nombre_archivo_en_configuracion():
    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()

    await _persistir(
        user_id=uuid.uuid4(),
        serie=[94.71, 89.83],
        timestamps=None,
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria="pico",
        etapas=[1],
        result=_etapa1_result_minimo(),
        etapa2_result=None,
        seleccion_etapa2=None,
        decisiones={},
        db=db,
        filename="estacion_04.csv",
    )

    # db.add() se llama dos veces (Analysis, AnalysisResult) — el primero
    # es el Analysis, donde vive configuracion.
    analysis_guardado = db.add.call_args_list[0].args[0]
    assert analysis_guardado.configuracion["nombre_archivo"] == "estacion_04.csv"
    # cramer_particion/mes_inicio_anio siguen ahí — F7a agrega una clave,
    # no reemplaza el dict.
    assert analysis_guardado.configuracion["cramer_particion"] == "default"
    assert analysis_guardado.configuracion["mes_inicio_anio"] == 7
    assert analysis_guardado.configuracion["variable_diaria"] == "pico"

"""
Tests unitarios del bloque "datos" nuevo de _serializar_etapa1() — PR 3 del
plan de cierre de pendientes no-test (docs/decisiones/decision058.md).

Los tres casos que DECISIÓN 058 distingue explícitamente:
- Carga anual: nada que agregar, serie_original/timestamps_originales/
  serie_calendario van None (peso muerto evitado, serían idénticos a los
  _efectiva).
- Carga mensual con mes_inicio_anio != 1: las dos agregaciones corren —
  serie_efectiva (con el mes configurado) y serie_calendario (mes_inicio=1,
  solo para presentación).
- Carga mensual con mes_inicio_anio == 1: la versión configurada YA ES la
  calendario — serie_calendario no se manda dos veces.
"""

import pytest

from metis.core.pipeline import ejecutar_etapa1
from metis.services.analysis_service import _serializar_etapa1


def _serie_anual(n: int = 40) -> tuple[list[float], list[int]]:
    serie = [50.0 + i * 1.3 for i in range(n)]
    timestamps = list(range(1970, 1970 + n))
    return serie, timestamps


def _serie_mensual(anios: int = 12) -> tuple[list[float], list[str]]:
    """`anios` calendario completos (ene-dic), valores crecientes
    determinísticos. Con exactamente años calendario completos, cualquier
    mes_inicio_anio != 1 recorta como mucho un período incompleto en cada
    extremo (nunca un hueco interior) y deja n >= 10 — sin disparar
    CONTRACT_SERIES_TOO_SHORT."""
    serie: list[float] = []
    timestamps: list[str] = []
    valor = 50.0
    for anio in range(2000, 2000 + anios):
        for mes in range(1, 13):
            timestamps.append(f"{anio:04d}-{mes:02d}-01")
            serie.append(valor)
            valor += 0.5
    return serie, timestamps


@pytest.mark.unit
def test_datos_carga_anual_no_manda_serie_original_ni_calendario():
    serie, timestamps = _serie_anual()
    result = ejecutar_etapa1(serie, "otro", "anual", timestamps=timestamps)

    datos = _serializar_etapa1(result, mes_inicio_anio=7)["datos"]

    assert datos["resolucion_original"] == "anual"
    assert datos["serie_original"] is None
    assert datos["timestamps_originales"] is None
    assert datos["serie_calendario"] is None
    assert datos["serie_efectiva"] == serie
    assert len(datos["timestamps_efectivos"]) == len(serie)
    assert datos["timestamps_efectivos"][0] == {"iso": "1970-01-01", "anio": 1970}


@pytest.mark.unit
def test_datos_carga_mensual_con_mes_inicio_distinto_de_1_manda_las_dos_agregaciones():
    serie, timestamps = _serie_mensual()
    result = ejecutar_etapa1(
        serie, "otro", "mensual", timestamps=timestamps, mes_inicio_anio=7
    )

    datos = _serializar_etapa1(result, mes_inicio_anio=7)["datos"]

    assert datos["resolucion_original"] == "mensual"
    # serie_original/timestamps_originales SÍ viajan — hubo agregación real.
    assert datos["serie_original"] == serie
    assert len(datos["timestamps_originales"]) == len(serie)
    assert datos["timestamps_originales"][0] == {"iso": "2000-01-01", "anio": 2000}

    # serie_efectiva: agregación con mes_inicio_anio=7 sobre 12 años
    # calendario completos (ene2000-dic2011). Períodos jul-jun cubiertos:
    # 1999 (solo ene-jun2000 presentes) y 2011 (solo jul-dic2011 presentes)
    # quedan incompletos en los extremos y se recortan; 2000..2010 (11
    # períodos) están completos.
    assert len(datos["serie_efectiva"]) == 11

    # serie_calendario: SEGUNDA agregación, mes_inicio=1, sobre los mismos
    # 12 años calendario ya completos de origen — sin nada que recortar,
    # 12 períodos. Necesariamente distinta de serie_efectiva (otro criterio
    # de año, otra cantidad de períodos) — por eso viaja con sus PROPIOS
    # timestamps, no como array suelto (corrección PR 4, ver docstring de
    # _calcular_serie_calendario()).
    assert datos["serie_calendario"] is not None
    assert len(datos["serie_calendario"]["serie"]) == 12
    assert len(datos["serie_calendario"]["timestamps"]) == 12
    assert datos["serie_calendario"]["timestamps"][0] == {
        "iso": "2000-01-01",
        "anio": 2000,
    }
    assert len(datos["serie_calendario"]["serie"]) != len(datos["serie_efectiva"])


@pytest.mark.unit
def test_datos_carga_mensual_con_mes_inicio_1_no_duplica_la_calendario():
    serie, timestamps = _serie_mensual()
    result = ejecutar_etapa1(
        serie, "otro", "mensual", timestamps=timestamps, mes_inicio_anio=1
    )

    datos = _serializar_etapa1(result, mes_inicio_anio=1)["datos"]

    assert datos["resolucion_original"] == "mensual"
    # mes_inicio_anio == 1 — la versión configurada YA ES la calendario, no
    # se manda una segunda vez.
    assert datos["serie_calendario"] is None
    # 12 años calendario completos, mes_inicio=1 — nada que recortar.
    assert len(datos["serie_efectiva"]) == 12


@pytest.mark.unit
def test_indice_atipico_va_null_sin_atipico_detectado():
    serie, timestamps = _serie_anual()
    result = ejecutar_etapa1(serie, "otro", "anual", timestamps=timestamps)

    datos = _serializar_etapa1(result, mes_inicio_anio=7)["datos"]

    assert datos["indice_atipico"] is None


@pytest.mark.unit
def test_datos_indice_atipico_coincide_con_test_result_dict():
    # Atípico evidente en la posición 20 (500.0 entre valores ~10) — mismo
    # patrón que tests/unit/services/test_analysis_service.py.
    serie = [10.0] * 20 + [500.0]
    result = ejecutar_etapa1(
        serie, "otro", "anual", timestamps=list(range(1980, 1980 + len(serie)))
    )

    payload = _serializar_etapa1(result, mes_inicio_anio=7)
    chow = next(t for t in payload["atipicos"] if t["prueba"] == "chow")

    # test_result_dict() ahora expone indice_atipico (ya existía en
    # TestResult, nunca se serializaba).
    assert chow["indice_atipico"] == 20
    # datos.indice_atipico ya viene en serie_efectiva-space — coincide con
    # el de la prueba porque valores_numericos ES serie_efectiva dentro de
    # ejecutar_etapa1() (DECISIÓN 058 §5), sin mapeo adicional.
    assert payload["datos"]["indice_atipico"] == 20

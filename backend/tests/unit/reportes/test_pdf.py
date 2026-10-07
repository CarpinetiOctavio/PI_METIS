"""
Tests unitarios del informe PDF (DECISIÓN 075) — metis/reportes/pdf.py.

El payload de entrada se arma con el pipeline y los serializadores reales
(`ejecutar_etapa1/2`, `_serializar_etapa1/2`), no a mano: si la forma de
`analysis_results` cambia, estos tests se enteran. Además del PDF completo
(bytes válidos), se inspecciona el texto de cada sección antes de maquetarlo
— el texto del PDF ya armado está codificado por subconjunto de glifos y no se
puede buscar sin una librería de lectura que el proyecto no tiene.
"""

import copy
import json

import numpy as np
import pytest
from reportlab.platypus import KeepTogether, Paragraph, Table

from metis.core.etapa2.design_events import calcular_eventos_diseno
from metis.core.pipeline import ejecutar_etapa1, ejecutar_etapa2
from metis.reportes.pdf import (
    _estilos,
    _registrar_fuentes,
    _seccion_datos,
    _seccion_etapa1,
    _seccion_etapa2,
    _seccion_simulacion,
    generar_pdf_analisis,
    nombre_archivo_pdf,
)
from metis.services.analysis_service import (
    _MODULOS_POR_DISTRIBUCION,
    _calcular_curva_ajuste,
    _serializar_etapa1,
    _serializar_etapa2,
)
from metis.services.export_service import (
    SimulacionNoDisponibleError,
    _simular_desde_detalle,
)

_PERIODOS = [2, 10, 100]


def _serie(n: int = 40) -> list[float]:
    rng = np.random.default_rng(7)
    return [round(float(v), 2) for v in rng.gumbel(100.0, 20.0, size=n)]


def _seleccion(etapa2_result, distribucion: str, metodo: str) -> dict:
    parametros = next(
        m.parametros
        for d in etapa2_result.ranking
        if d.distribucion == distribucion
        for m in d.metodos
        if m.metodo == metodo
    )
    modulo = _MODULOS_POR_DISTRIBUCION[distribucion]
    eventos = calcular_eventos_diseno(modulo, parametros, _PERIODOS)
    curva = _calcular_curva_ajuste(
        modulo,
        parametros,
        _PERIODOS,
        max(p.periodo_retorno for p in etapa2_result.puntos_empiricos),
    )
    return {
        "distribucion": distribucion,
        "metodo": metodo,
        "periodos_retorno": _PERIODOS,
        "eventos_diseno": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor} for e in eventos
        ],
        "curva_ajuste": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor} for e in curva
        ],
    }


def _detalle(
    etapas: tuple[int, ...] = (1, 2),
    con_seleccion: bool = True,
    serie: list[float] | None = None,
) -> dict:
    """Misma forma que get_analysis_by_id(), pasada por JSON como si saliera
    de las columnas JSONB."""
    serie = serie if serie is not None else _serie()
    timestamps = [f"{1980 + i}-01-01" for i in range(len(serie))]
    r1 = ejecutar_etapa1(serie, "caudal_precipitacion", "anual", timestamps)
    etapa2 = None
    if 2 in etapas and r1.nivel_confianza != "rechazado":
        r2 = ejecutar_etapa2(np.array(r1.serie_efectiva, dtype=float))
        seleccion = _seleccion(r2, "gumbel", "momentos") if con_seleccion else None
        etapa2 = _serializar_etapa2(r2, seleccion)
    detalle = {
        "id": "00000000-0000-0000-0000-000000000001",
        "tipo_variable": "caudal_precipitacion",
        "modo": "paso_a_paso",
        "etapas": [str(e) for e in etapas],
        "created_at": "2026-10-06T12:00:00",
        "etapa1": _serializar_etapa1(r1, 7),
        "etapa2": etapa2,
        "decisiones": {},
        "serie": serie,
        "timestamps": [{"iso": t, "anio": int(t[:4])} for t in timestamps],
        "configuracion": {
            "cramer_particion": "default",
            "mes_inicio_anio": 7,
            "variable_diaria": "pico",
            "nombre_archivo": "estación 04.csv",
        },
    }
    return json.loads(json.dumps(detalle))


def _textos(flowables) -> list[str]:
    textos = []
    for f in flowables:
        if isinstance(f, Paragraph):
            textos.append(f.getPlainText())
        elif isinstance(f, Table):
            for fila in f._cellvalues:
                textos.append(" | ".join(" ".join(_textos([c])) for c in fila))
        elif isinstance(f, KeepTogether):
            textos += _textos(f._content)
    return textos


@pytest.fixture(scope="module")
def est():
    _registrar_fuentes()
    return _estilos()


@pytest.fixture(scope="module")
def detalle_completo() -> dict:
    return _detalle()


def _es_pdf(contenido: bytes) -> bool:
    return contenido.startswith(b"%PDF-") and b"%%EOF" in contenido[-1024:]


@pytest.mark.unit
def test_pdf_etapa1_y_etapa2_es_un_pdf_valido(detalle_completo):
    assert _es_pdf(generar_pdf_analisis(detalle_completo, autor="Docente"))


@pytest.mark.unit
def test_pdf_solo_etapa1_no_tiene_seccion_de_etapa2(est):
    detalle = _detalle(etapas=(1,))

    assert _es_pdf(generar_pdf_analisis(detalle))
    assert _seccion_etapa2(detalle, est) == []
    textos = _textos(_seccion_etapa1(detalle, est))
    assert any("Independencia" in t for t in textos)
    assert any(t.startswith("Anderson |") for t in textos)


@pytest.mark.unit
def test_ranking_completo_sin_ganadora_y_con_la_elegida_resaltada(
    detalle_completo, est
):
    seccion = _seccion_etapa2(detalle_completo, est)
    textos = _textos(seccion)
    tabla = next(
        f
        for f in seccion
        if isinstance(f, Table) and _textos([f])[0].startswith("# | Distribución")
    )
    filas = _textos([tabla])[1:]

    assert len(filas) == 13
    elegidas = [f for f in filas if "Elegida por el usuario" in f]
    assert len(elegidas) == 1 and "Gumbel" in elegidas[0]
    assert not any("recomend" in t.lower() or "ganador" in t.lower() for t in textos)
    pareto = next(f for f in filas if "Generalizada de Pareto" in f)
    assert "Pendiente de validación" in pareto


@pytest.mark.unit
def test_eventos_de_diseno_de_la_eleccion(detalle_completo, est):
    textos = _textos(_seccion_etapa2(detalle_completo, est))
    eventos = detalle_completo["etapa2"]["seleccion"]["eventos_diseno"]

    assert any(t.startswith("Distribución | Gumbel") for t in textos)
    for e in eventos:
        assert any(
            t.startswith(f"{e['periodo_retorno']} |") and f"{e['valor']:.4f}" in t
            for t in textos
        )


@pytest.mark.unit
def test_etapa2_sin_eleccion_registrada_lo_avisa(est):
    detalle = _detalle(con_seleccion=False)

    assert _es_pdf(generar_pdf_analisis(detalle))
    textos = _textos(_seccion_etapa2(detalle, est))
    assert any("No quedó registrada ninguna distribución elegida" in t for t in textos)
    assert not any("Elegida por el usuario" in t for t in textos)


@pytest.mark.unit
def test_etapa1_rechazada_por_contrato(est):
    detalle = _detalle(serie=[10.0, 12.0, 11.0, 14.0, 13.0])

    assert detalle["etapa1"]["nivel_confianza"] == "rechazado"
    assert _es_pdf(generar_pdf_analisis(detalle))
    etapa1 = _textos(_seccion_etapa1(detalle, est))
    assert any("CONTRACT_SERIES_TOO_SHORT" in t for t in etapa1)
    assert not any("Estadística descriptiva" in t for t in etapa1)
    etapa2 = _textos(_seccion_etapa2(detalle, est))
    assert any("Etapa 2 no se ejecutó" in t for t in etapa2)


@pytest.mark.unit
def test_formato_experto_no_muestra_formulas(detalle_completo, est):
    # El análisis se corrió en paso a paso y su payload trae `explicacion` con
    # ecuaciones y términos; el PDF es siempre Experto y no los usa.
    anderson = detalle_completo["etapa1"]["independencia"][0]
    assert anderson["explicacion"]["ecuacion"]

    textos = _textos(
        _seccion_etapa1(detalle_completo, est) + _seccion_etapa2(detalle_completo, est)
    )
    assert not any(anderson["explicacion"]["ecuacion"] in t for t in textos)
    assert not any("Ec." in t or "ecuación" in t.lower() for t in textos)


@pytest.mark.unit
def test_decision_ante_atipico(detalle_completo, est):
    detalle = copy.deepcopy(detalle_completo)
    detalle["decisiones"] = {"chow": {"accion": "rechazar", "dato": 950.0}}

    textos = _textos(_seccion_etapa1(detalle, est))
    assert any("950.0000" in t and "rechazó" in t for t in textos)


@pytest.mark.unit
def test_analisis_anterior_sin_datos_ni_desglose(detalle_completo):
    # Registros previos a DECISIÓN 058 / addendum de la 064: sin `datos`,
    # sin `desglose` y sin `timestamps` — se exporta igual, sin gráficos.
    detalle = copy.deepcopy(detalle_completo)
    del detalle["etapa1"]["datos"]
    for tr in detalle["etapa1"]["independencia"]:
        if tr["explicacion"]:
            tr["explicacion"].pop("desglose", None)
    detalle["timestamps"] = None
    detalle["configuracion"] = None

    assert _es_pdf(generar_pdf_analisis(detalle))


@pytest.mark.unit
def test_datos_del_analisis(detalle_completo, est):
    textos = _textos(_seccion_datos(detalle_completo, "Ana (ana@ucc.edu.ar)", est))

    assert "Archivo | estación 04.csv" in textos
    assert "Usuario | Ana (ana@ucc.edu.ar)" in textos
    assert "Etapas ejecutadas | Etapa 1 y Etapa 2" in textos
    assert "Inicio del año | Julio" in textos
    assert "Partición de Cramer | Por defecto (60 % / 30 %)" in textos


@pytest.mark.unit
def test_nombre_archivo_pdf_ascii():
    detalle = {
        "created_at": "2026-10-06T12:00:00",
        "configuracion": {"nombre_archivo": "Estación Río Cuarto (1980-2019).xlsx"},
    }
    assert (
        nombre_archivo_pdf(detalle)
        == "metis_Estacion_Rio_Cuarto_1980-2019_2026-10-06.pdf"
    )


@pytest.mark.unit
def test_nombre_archivo_pdf_sin_nombre_registrado():
    detalle = {"created_at": "2026-10-06T12:00:00", "configuracion": None}
    assert nombre_archivo_pdf(detalle) == "metis_analisis_2026-10-06.pdf"


# --- Simulación sin los puntos excluidos (DECISIÓN 075, addendum) -----------


def _indice_maximo(detalle: dict) -> int:
    serie = detalle["etapa1"]["datos"]["serie_efectiva"]
    return max(range(len(serie)), key=lambda i: serie[i])


@pytest.mark.unit
def test_simulacion_compara_con_y_sin_los_puntos(detalle_completo, est):
    indice = _indice_maximo(detalle_completo)
    simulacion = _simular_desde_detalle(detalle_completo, [indice])

    assert _es_pdf(generar_pdf_analisis(detalle_completo, simulacion=simulacion))

    seccion = _seccion_simulacion(detalle_completo, simulacion, est)
    textos = _textos(seccion)
    excluido = simulacion["excluidos"][0]
    assert any(
        f"Se quitó: {excluido['periodo']} ({excluido['valor_original']:.4f})" in t
        and "Datos: 40 → 39" in t
        for t in textos
    )
    tabla_pruebas = next(
        f
        for f in seccion
        if isinstance(f, Table) and _textos([f])[0].startswith("Prueba | Grupo")
    )
    assert len(_textos([tabla_pruebas])) == 1 + 8
    assert any("Ranking de distribuciones sin esos puntos" in t for t in textos)
    # La elección original reajustada: una fila por período, con la diferencia.
    tabla_eventos = next(
        f
        for f in seccion
        if isinstance(f, Table) and _textos([f])[0].endswith("Diferencia")
    )
    filas = _textos([tabla_eventos])[1:]
    assert len(filas) == len(_PERIODOS)
    assert all(f.endswith("%") for f in filas)


@pytest.mark.unit
def test_simulacion_toma_la_entrada_del_analisis_persistido(detalle_completo):
    # Del cliente llegan solo los índices: serie, años, configuración y la
    # elección salen del análisis guardado.
    simulacion = _simular_desde_detalle(detalle_completo, [0])

    serie = detalle_completo["etapa1"]["datos"]["serie_efectiva"]
    assert simulacion["serie"] == serie[1:]
    assert simulacion["anios"][0] == 1981
    seleccion = simulacion["etapa2"]["seleccion"]
    assert (seleccion["distribucion"], seleccion["metodo"]) == ("gumbel", "momentos")
    assert [e["periodo_retorno"] for e in seleccion["eventos_diseno"]] == _PERIODOS


@pytest.mark.unit
def test_simulacion_que_deja_la_serie_bloqueada(est):
    detalle = _detalle(etapas=(1,), serie=_serie(11))
    simulacion = _simular_desde_detalle(detalle, [0, 1])

    assert simulacion["etapa1"]["contract"]["bloqueante"]
    assert _es_pdf(generar_pdf_analisis(detalle, simulacion=simulacion))
    textos = _textos(_seccion_simulacion(detalle, simulacion, est))
    assert any("CONTRACT_SERIES_TOO_SHORT" in t for t in textos)
    assert not any(t.startswith("Prueba | Grupo") for t in textos)


@pytest.mark.unit
def test_simulacion_no_disponible_sin_la_serie_analizada(detalle_completo):
    detalle = copy.deepcopy(detalle_completo)
    del detalle["etapa1"]["datos"]

    with pytest.raises(SimulacionNoDisponibleError):
        _simular_desde_detalle(detalle, [0])


@pytest.mark.unit
def test_nombre_archivo_pdf_con_simulacion():
    detalle = {"created_at": "2026-10-06T12:00:00", "configuracion": None}
    assert (
        nombre_archivo_pdf(detalle, simulacion=True)
        == "metis_analisis_2026-10-06_simulacion.pdf"
    )

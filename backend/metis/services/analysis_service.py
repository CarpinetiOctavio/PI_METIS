import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metis.core.etapa1.significancia import ALFA_DEFECTO
from metis.core.etapa2.design_events import calcular_eventos_diseno
from metis.core.etapa2.types import Etapa2Result, EventoDiseno
from metis.core.pipeline import ejecutar_etapa1, ejecutar_etapa2
from metis.core.pipeline.exclusiones import aplicar_exclusiones
from metis.core.pipeline.pipeline_etapa1 import CODIGOS_WARNING_AGREGACION
from metis.core.pipeline.pipeline_etapa2 import _DISTRIBUCIONES
from metis.core.types import Etapa1Result
from metis.core.utils import es_numerico, filtrar_numericos
from metis.core.validacion.aggregation import (
    COBERTURA_MINIMA_INTERIOR,
    agregar_a_maximos_anuales,
    agregar_a_maximos_mensuales,
)
from metis.core.validacion.parser import parse_file, parsear_timestamps
from metis.db.models import Analysis, AnalysisResult
from metis.services import session_store

_MODULOS_POR_DISTRIBUCION = dict(_DISTRIBUCIONES)


class MetodoNoAjustadoError(Exception):
    """La combinación distribución+método pedida no tiene parámetros
    ajustados en el ranking persistido (no está, o status != 'ok') —
    Bloque C2c, DECISIÓN 062. El borde del endpoint la traduce a 400
    DIST_METHOD_NOT_FITTED."""


def _sse(tipo: str, payload: dict) -> str:
    return f"event: {tipo}\ndata: {json.dumps(payload)}\n\n"


def _serializar_timestamps(
    timestamps: list | None, *, agregados: bool
) -> list[dict] | None:
    """Normaliza timestamps_efectivos/timestamps_originales a una forma
    única — PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058,
    §4.4). Sin agregación es la lista cruda del parser (str/int/pd.Timestamp
    heterogéneos); agregada es list[int] (año-etiqueta de
    agregar_a_maximos_anuales()). Serializar cualquiera de las dos tal cual
    manda JSON inconsistente al frontend según de dónde vino el archivo —
    acá siempre se emite ISO-8601 str, más `anio` como campo propio para que
    el gráfico de serie anual rotule por año, no por fecha completa.
    """
    if timestamps is None:
        return None
    if agregados:
        return [{"iso": f"{anio}-01-01", "anio": int(anio)} for anio in timestamps]
    parsed = parsear_timestamps(timestamps)
    return [{"iso": ts.strftime("%Y-%m-%d"), "anio": int(ts.year)} for ts in parsed]


def _calcular_serie_calendario(
    result: Etapa1Result, mes_inicio_anio: int
) -> dict | None:
    """Segunda agregación, mes_inicio=1, SOLO para presentación — DECISIÓN
    058 §3. No toca Etapa1Result ni ninguna prueba estadística, corre aparte
    después de que Etapa 1 ya terminó. None si no hubo agregación real
    (carga anual, nada que comparar) o si mes_inicio_anio ya es 1 (la
    versión configurada YA ES la calendario, no se manda dos veces lo
    mismo).

    Corrección PR 4 (encontrada al construir el gráfico consumidor): DECISIÓN
    058 documentaba esto como `list[float]` bareback, asumiendo implícitamente
    que tendría el mismo largo que serie_efectiva. Falso — la agregación
    calendario recorta sus propios extremos parciales de forma independiente
    (otro mes_inicio, otro criterio de qué período queda completo), así que
    puede tener MÁS o MENOS puntos que serie_efectiva. Sin sus propios
    timestamps no hay forma de ubicar cada valor en el eje X — se devuelve
    `{serie, timestamps}`, no un array suelto.
    """
    if result.resolucion_original not in ("mensual", "diaria") or mes_inicio_anio == 1:
        return None
    # R3.4 (docs/historico/planes/plan-resolucion-diaria.md) — `resolucion=` es OBLIGATORIO.
    # Sin él, con los defaults de agregar_a_maximos_anuales() esta segunda
    # agregación correría en modo "mensual" sobre datos diarios: la clave de
    # agrupación sería (año, mes), la asignación sobreescribe, y
    # serie_calendario terminaría siendo el máximo de los últimos días de
    # cada mes — silencioso, plausible y equivocado. Corre sobre
    # result.serie_original (la serie DIARIA cruda, no la agregación mensual
    # del payload) — el camino directo diaria → anual, el mismo que la serie
    # configurada, para no comparar dos series calculadas con métodos
    # distintos en el mismo gráfico (R0.3).
    agregacion = agregar_a_maximos_anuales(
        result.serie_original,
        result.timestamps_originales,
        mes_inicio=1,
        resolucion=result.resolucion_original,
        cobertura_minima_interior=COBERTURA_MINIMA_INTERIOR[result.resolucion_original],
    )
    return {
        "serie": agregacion.serie,
        "timestamps": _serializar_timestamps(agregacion.timestamps, agregados=True),
    }


def _serializar_etapa1(result: Etapa1Result, mes_inicio_anio: int) -> dict:
    """mes_inicio_anio como segundo argumento, no `parsed: ParsedData`
    completo (alternativa evaluada y descartada — PR 3 del plan de cierre
    de pendientes no-test): _persistir() también llama a esta función, y
    arrastrar el ParsedData completo por los dos caminos solo para leer un
    entero sería peor que el problema que resuelve. serie_original/
    timestamps_originales/resolucion_original SÍ viajan enteros dentro de
    `result` (Etapa1Result los expone desde DECISIÓN 058) — mes_inicio_anio
    es la única pieza que Etapa1Result no tiene motivo para cargar (es un
    parámetro del request, no del análisis en sí).
    """

    def test_result_dict(tr) -> dict:
        return {
            "prueba": tr.prueba,
            "estadistico": tr.estadistico,
            "valor_critico": tr.valor_critico,
            "veredicto": tr.veredicto,
            "warning_codigo": tr.warning_codigo,
            "warning_nivel": tr.warning_nivel,
            "n1": tr.n1,
            "n2": tr.n2,
            "valor_atipico": tr.valor_atipico,
            "indice_atipico": tr.indice_atipico,
            # DECISIÓN 079 — Chow: todos los valores fuera de los umbrales.
            "valores_atipicos": tr.valores_atipicos,
            # Bloque D (plan post-avance, DECISIÓN 064) — piezas para la
            # fórmula sustituida en modo paso a paso. None para pruebas
            # "no_ejecutada" (nada que sustituir).
            "explicacion": (
                {
                    "ecuacion": tr.explicacion.ecuacion,
                    "terminos": tr.explicacion.terminos,
                    # Addendum 01/10/2026 a la DECISIÓN 064 — Anderson y Chow.
                    "desglose": tr.explicacion.desglose,
                }
                if tr.explicacion
                else None
            ),
        }

    def warning_dict(w) -> dict:
        return {"codigo": w.codigo, "nivel": w.nivel, "descripcion": w.descripcion}

    hubo_agregacion = result.resolucion_original in ("mensual", "diaria")

    # Bloque F5/PR3 (DECISIÓN 058 §5) — indice_atipico ya viaja en
    # serie_efectiva-space: calcular_chow() corre sobre valores_numericos,
    # que dentro de ejecutar_etapa1() ES serie_efectiva (misma lista, sin
    # otro filtrado de por medio). No hace falta un mapeo adicional acá.
    indice_atipico = _extraer_indice_atipico(result)

    # R3.3 opción 2 (docs/historico/planes/plan-resolucion-diaria.md) — qué serie cruda viaja
    # en el payload y a qué resolución. Con carga diaria NO se serializa la
    # serie diaria cruda (~14.600 ítems, ~637 KB — contradice el
    # dimensionamiento de DECISIÓN 058): se serializa la agregación a
    # máximos MENSUALES (~480 ítems). `resolucion_serie_original` le dice al
    # frontend a qué resolución está `serie_original` — distinto de
    # `resolucion_original` (la del archivo). El rótulo del boxplot
    # ("máximos mensuales agregados desde datos diarios") es responsabilidad
    # del frontend (PR 3). Etapa1Result.serie_original NO se toca: sigue
    # siendo la serie diaria cruda que alimenta _calcular_serie_calendario().
    if result.resolucion_original == "diaria":
        serie_original_payload, timestamps_originales_payload = (
            agregar_a_maximos_mensuales(
                result.serie_original, result.timestamps_originales
            )
        )
        resolucion_serie_original = "mensual"
    elif result.resolucion_original == "mensual":
        serie_original_payload = result.serie_original
        timestamps_originales_payload = result.timestamps_originales
        resolucion_serie_original = "mensual"
    else:
        # Carga anual — serie_original es idéntica a serie_efectiva,
        # duplicarla es peso muerto (DECISIÓN 058 §1).
        serie_original_payload = None
        timestamps_originales_payload = None
        resolucion_serie_original = result.resolucion_original

    datos = {
        "resolucion_original": result.resolucion_original,
        "resolucion_serie_original": resolucion_serie_original,
        "serie_efectiva": result.serie_efectiva,
        "timestamps_efectivos": _serializar_timestamps(
            result.timestamps_efectivos, agregados=hubo_agregacion
        ),
        "serie_original": serie_original_payload,
        "timestamps_originales": (
            _serializar_timestamps(timestamps_originales_payload, agregados=False)
            if timestamps_originales_payload is not None
            else None
        ),
        "indice_atipico": indice_atipico,
        "serie_calendario": _calcular_serie_calendario(result, mes_inicio_anio),
    }

    return {
        "contract": {
            "bloqueante": result.contract.bloqueante,
            "codigo_error": result.contract.codigo_error,
            "warnings": [warning_dict(w) for w in result.contract.warnings],
        },
        "descriptive": (
            {
                "n": result.descriptive.n,
                "media": result.descriptive.media,
                "mediana": result.descriptive.mediana,
                "desvio_estandar": result.descriptive.desvio_estandar,
                "coef_variacion": result.descriptive.coef_variacion,
                "coef_asimetria": result.descriptive.coef_asimetria,
                "minimo": result.descriptive.minimo,
                "maximo": result.descriptive.maximo,
            }
            if result.descriptive
            else None
        ),
        "independencia": [test_result_dict(t) for t in result.independencia],
        "homogeneidad": [test_result_dict(t) for t in result.homogeneidad],
        "tendencia": [test_result_dict(t) for t in result.tendencia],
        "atipicos": [test_result_dict(t) for t in result.atipicos],
        "nivel_independencia": result.nivel_independencia,
        "nivel_homogeneidad": result.nivel_homogeneidad,
        "nivel_confianza": result.nivel_confianza,
        "warnings": [warning_dict(w) for w in result.warnings],
        "datos": datos,
        # DECISIÓN 078 — con qué nivel de significancia corrió la batería.
        "alfa": result.alfa,
    }


def _serializar_etapa2(result: Etapa2Result, seleccion: dict | None = None) -> dict:
    """Hermana exacta de _serializar_etapa1() (DECISIÓN 055, Bloque A5).

    Serializa la grilla completa — las 13 distribuciones con TODOS sus
    métodos, incluidos no_converge/no_aplicable/disabled_zeros. No aplana
    a un top-3: la tesis misma reporta que ciertas combinaciones no
    convergen, y eso es información docente, no un error a esconder.

    `seleccion` (Bloque C2a, plan post-avance) — la elección de
    distribución+método del usuario y sus resultados (eventos_diseno,
    curva_ajuste), para que el historial pueda mostrarla sin recalcular
    nada. `None` cuando no se llegó a elegir (stream abandonado en la
    pausa, o `result_etapa2_ranking` — se emite ANTES de que exista
    ninguna elección) — mismo criterio sin backfill que `timestamps`
    (DECISIÓN 058 §4) y `nombre_archivo` (F7a): el campo siempre está
    presente en el JSON, en `null` cuando no aplica.
    """

    def metodo_dict(m) -> dict:
        return {
            "metodo": m.metodo,
            "parametros": m.parametros,
            "eea": m.eea,
            "status": m.status,
        }

    def dist_dict(d) -> dict:
        return {
            "distribucion": d.distribucion,
            "n_parametros": d.n_parametros,
            "metodos": [metodo_dict(m) for m in d.metodos],
            "mejor_eea": d.mejor_eea,
            "mejor_metodo": d.mejor_metodo,
            "pendiente_validacion": d.pendiente_validacion,
        }

    def warning_dict(w) -> dict:
        return {"codigo": w.codigo, "nivel": w.nivel, "descripcion": w.descripcion}

    def punto_empirico_dict(p) -> dict:
        return {
            "valor": p.valor,
            "periodo_retorno": p.periodo_retorno,
            "probabilidad": p.probabilidad,
        }

    return {
        "ranking": [dist_dict(d) for d in result.ranking],
        "warnings": [warning_dict(w) for w in result.warnings],
        # Bloque C — insumo del gráfico de ajuste (puntos empíricos vs.
        # curva). Independiente de la distribución elegida, ver
        # PuntoEmpirico en core/etapa2/types.py.
        "puntos_empiricos": [punto_empirico_dict(p) for p in result.puntos_empiricos],
        "seleccion": seleccion,
    }


def _calcular_curva_ajuste(
    modulo, parametros: dict, periodos_retorno: list[float], max_t_empirico: float
) -> list[EventoDiseno]:
    """Muestreo denso de 60 puntos en escala logarítmica para el gráfico de
    ajuste — compartido entre stream_analysis() (Bloque C) y
    recalcular_eventos_diseno() (Bloque C2c, historial interactivo). No son
    los T que pidió el usuario (eventos_diseno ya los cubre): cubre desde
    T=1.05 hasta el mayor entre el T pedido y el T empírico máximo de la
    muestra, para que la curva tape el mismo rango que los puntos
    empíricos del gráfico de ajuste.
    """
    t_max_curva = max(max(periodos_retorno, default=1.05), max_t_empirico)
    periodos_curva = np.geomspace(1.05, max(t_max_curva, 1.06), num=60).tolist()
    return calcular_eventos_diseno(modulo, parametros, periodos_curva)


def _emitir_resultado(result: Etapa1Result, iteracion: int) -> list[str]:
    """Genera la secuencia de eventos SSE para un Etapa1Result completo."""
    eventos: list[str] = []
    total_pasos = 8  # contrato, descriptiva, anderson, wald, helmert, t_student+cramer, mann_kendall+ks, chow
    completado = 0

    # Contrato
    completado += 1
    if result.contract.bloqueante:
        eventos.append(
            _sse(
                "contract_error",
                {
                    "codigo": result.contract.codigo_error,
                    "iteracion": iteracion,
                },
            )
        )
        return eventos

    for w in result.contract.warnings:
        eventos.append(
            _sse(
                "contract_warning",
                {"codigo": w.codigo, "nivel": w.nivel, "iteracion": iteracion},
            )
        )

    # Descriptiva
    completado += 1
    if result.descriptive:
        eventos.append(
            _sse(
                "descriptive_stats",
                {
                    "n": result.descriptive.n,
                    "media": result.descriptive.media,
                    "mediana": result.descriptive.mediana,
                    "desvio_estandar": result.descriptive.desvio_estandar,
                    "coef_variacion": result.descriptive.coef_variacion,
                    "coef_asimetria": result.descriptive.coef_asimetria,
                    "minimo": result.descriptive.minimo,
                    "maximo": result.descriptive.maximo,
                    "iteracion": iteracion,
                },
            )
        )

    # Independencia
    for prueba in result.independencia:
        completado += 1
        eventos.append(
            _sse(
                "progress",
                {
                    "paso": prueba.prueba,
                    "etapa": 1,
                    "completado": completado,
                    "total": total_pasos,
                    "iteracion": iteracion,
                },
            )
        )
        d = {
            "prueba": prueba.prueba,
            "estadistico": prueba.estadistico,
            "valor_critico": prueba.valor_critico,
            "veredicto": prueba.veredicto,
            "warning_codigo": prueba.warning_codigo,
            "warning_nivel": prueba.warning_nivel,
            "n1": prueba.n1,
            "n2": prueba.n2,
            "valor_atipico": prueba.valor_atipico,
            "indice_atipico": prueba.indice_atipico,
            "iteracion": iteracion,
        }
        eventos.append(_sse("test_result", d))

    # Homogeneidad
    for prueba in result.homogeneidad:
        completado += 1
        eventos.append(
            _sse(
                "progress",
                {
                    "paso": prueba.prueba,
                    "etapa": 1,
                    "completado": completado,
                    "total": total_pasos,
                    "iteracion": iteracion,
                },
            )
        )
        d = {
            "prueba": prueba.prueba,
            "estadistico": prueba.estadistico,
            "valor_critico": prueba.valor_critico,
            "veredicto": prueba.veredicto,
            "warning_codigo": prueba.warning_codigo,
            "warning_nivel": prueba.warning_nivel,
            "n1": prueba.n1,
            "n2": prueba.n2,
            "valor_atipico": prueba.valor_atipico,
            "indice_atipico": prueba.indice_atipico,
            "iteracion": iteracion,
        }
        eventos.append(_sse("test_result", d))

    # Tendencia
    for prueba in result.tendencia:
        completado += 1
        eventos.append(
            _sse(
                "progress",
                {
                    "paso": prueba.prueba,
                    "etapa": 1,
                    "completado": completado,
                    "total": total_pasos,
                    "iteracion": iteracion,
                },
            )
        )
        d = {
            "prueba": prueba.prueba,
            "estadistico": prueba.estadistico,
            "valor_critico": prueba.valor_critico,
            "veredicto": prueba.veredicto,
            "warning_codigo": prueba.warning_codigo,
            "warning_nivel": prueba.warning_nivel,
            "n1": prueba.n1,
            "n2": prueba.n2,
            "valor_atipico": prueba.valor_atipico,
            "indice_atipico": prueba.indice_atipico,
            "iteracion": iteracion,
        }
        eventos.append(_sse("test_result", d))

    # Atípicos
    for prueba in result.atipicos:
        completado += 1
        eventos.append(
            _sse(
                "progress",
                {
                    "paso": prueba.prueba,
                    "etapa": 1,
                    "completado": completado,
                    "total": total_pasos,
                    "iteracion": iteracion,
                },
            )
        )
        d = {
            "prueba": prueba.prueba,
            "estadistico": prueba.estadistico,
            "valor_critico": prueba.valor_critico,
            "veredicto": prueba.veredicto,
            "warning_codigo": prueba.warning_codigo,
            "warning_nivel": prueba.warning_nivel,
            "n1": prueba.n1,
            "n2": prueba.n2,
            "valor_atipico": prueba.valor_atipico,
            "indice_atipico": prueba.indice_atipico,
            "iteracion": iteracion,
        }
        eventos.append(_sse("test_result", d))

    return eventos


class DecisionAtipicoInvalidaError(ValueError):
    """outlier-decision no decide exactamente los atípicos de la pausa
    (DECISIÓN 079). El borde la traduce a 400 OUTLIER_DECISION_INVALID."""


def _atipicos_para_decidir(result: Etapa1Result) -> list[dict]:
    """Los atípicos de Chow de la primera pasada, con su año, para la pausa
    (DECISIÓN 079). `indice` es la posición en serie_efectiva, la misma que
    usa la exclusión de puntos (DECISIÓN 071)."""
    chow = next((p for p in result.atipicos if p.prueba == "chow"), None)
    if chow is None or not chow.valores_atipicos:
        return []
    hubo_agregacion = result.resolucion_original in ("mensual", "diaria")
    timestamps = _serializar_timestamps(
        result.timestamps_efectivos, agregados=hubo_agregacion
    )
    return [
        {
            "indice": a["indice"],
            "periodo": timestamps[a["indice"]]["anio"] if timestamps else None,
            "valor": a["valor"],
            "z": a["z"],
            "lado": a["lado"],
        }
        for a in chow.valores_atipicos
    ]


def _describir_chow_tras_decision(
    result: Etapa1Result, decisiones_chow: list[dict], hubo_rechazos: bool
) -> None:
    """Reescribe el warning de Chow del resultado final, que ya no está
    "pendiente de decisión" (DECISIÓN 079). Si la segunda pasada, sin los
    rechazados, encuentra valores NUEVOS fuera de los umbrales, lo dice: no se
    vuelve a pausar y quedan sugeridos en el panel de exclusión."""
    aceptados = [a for a in decisiones_chow if a["decision"] == "aceptar"]
    claves_aceptados = {(a["periodo"], a["valor"]) for a in aceptados}
    nuevos = [
        a
        for a in _atipicos_para_decidir(result)
        if (a["periodo"], a["valor"]) not in claves_aceptados
    ]

    def anios(lista: list[dict]) -> str:
        return ", ".join(str(a["periodo"]) for a in lista if a["periodo"] is not None)

    for w in result.warnings:
        if w.codigo != "TEST_WARNING_OUTLIER_DETECTED":
            continue
        if hubo_rechazos and nuevos:
            w.descripcion = (
                f"Sin los atípicos rechazados, Chow encuentra {len(nuevos)} valor(es) nuevo(s) "
                f"fuera de los umbrales ({anios(nuevos)}). No se vuelve a pausar: quedan "
                "sugeridos en el panel de exclusión de puntos."
            )
        elif aceptados:
            w.descripcion = (
                "Chow detectó valores fuera de los umbrales que aceptaste como parte de "
                f"la población ({anios(aceptados)})."
            )


def _extraer_atipico(result: Etapa1Result) -> float | None:
    """Retorna el valor atípico de Chow si fue detectado, None si no."""
    for prueba in result.atipicos:
        if prueba.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED":
            return prueba.valor_atipico
    return None


def _extraer_indice_atipico(result: Etapa1Result) -> int | None:
    """Retorna el índice del atípico de Chow si fue detectado, None si no.

    Este índice está calculado por calcular_chow() sobre valores_numericos
    (la serie ya filtrada por filtrar_numericos() dentro de ejecutar_etapa1()),
    no sobre la serie cruda. Usar _mapear_indice_a_serie_original() antes de
    aplicarlo sobre serie_original.
    """
    for prueba in result.atipicos:
        if prueba.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED":
            return prueba.indice_atipico
    return None


def _mapear_indice_a_serie_original(indice_filtrado: int, serie_original: list) -> int:
    """Traduce un índice calculado sobre la serie filtrada (solo valores
    numéricos, mismo criterio que filtrar_numericos/es_numerico) a la
    posición real correspondiente en serie_original.

    serie_original puede tener None u otros valores no numéricos
    intercalados (valores Y faltantes) que filtrar_numericos() descarta
    antes de correr las pruebas de Etapa 1 — sin este mapeo, el índice
    que devuelve Chow queda desalineado respecto de serie_original en
    cuanto hay algún valor no numérico antes de la posición del atípico.
    """
    indices_numericos = [i for i, v in enumerate(serie_original) if es_numerico(v)]
    return indices_numericos[indice_filtrado]


async def stream_analysis(
    content: bytes,
    filename: str,
    columna_x: str,
    columna_y: str,
    tipo_variable: str,
    modo: str,
    cramer_particion: dict | str,
    etapas: list[int],
    session_id: str,
    user_id: uuid.UUID | None,
    db: AsyncSession,
    mes_inicio_anio: int = 7,
    variable_diaria: str = "pico",
    alfa: float = ALFA_DEFECTO,
) -> AsyncGenerator[str, None]:
    # DECISIÓN 054 — etapas ya llega validado y parseado desde el borde del
    # endpoint. Con etapas == [1] todo lo de abajo se comporta exactamente
    # igual que antes de que Etapa 2 existiera.
    session_store.create_session(session_id)
    analysis_id: uuid.UUID | None = None

    try:
        # Parsear archivo
        try:
            parsed = parse_file(content, filename, columna_x, columna_y)
        except Exception as exc:
            yield _sse("error", {"codigo": "PARSE_ERROR", "mensaje": str(exc)})
            return

        serie_original = parsed.serie

        # Primera ejecución
        result = ejecutar_etapa1(
            serie=serie_original,
            tipo_variable=tipo_variable,
            resolucion_temporal=parsed.resolucion_temporal,
            timestamps=parsed.timestamps,
            cramer_particion=cramer_particion,
            mes_inicio_anio=mes_inicio_anio,
            variable_diaria=variable_diaria,
            alfa=alfa,
        )

        for evento in _emitir_resultado(result, iteracion=1):
            yield evento

        if result.contract.bloqueante:
            yield _sse("complete", {"analysis_id": None})
            return

        # Bloque F4 — de acá en más, todo lo que sigue (mapeo de índice de
        # Chow, Etapa 2) razona sobre serie_efectiva: la serie tal como
        # ejecutar_etapa1() la analizó de verdad — igual a serie_original si
        # resolucion_temporal era "anual" (nada que agregar), o los máximos
        # anuales agregados si era "mensual". serie_original en sí NO se
        # reasigna: sigue siendo la serie cruda tal como se subió, para
        # _persistir() más abajo (auditoría de lo que el usuario subió, no
        # de lo que se analizó).
        serie_efectiva = result.serie_efectiva
        timestamps_efectivos = result.timestamps_efectivos

        # Chow detectó atípicos — pausar y esperar decisión (CU-01 y CU-02).
        # DECISIÓN 079: una sola pausa con TODOS los valores fuera de los
        # umbrales, y una decisión por punto.
        valor_atipico = _extraer_atipico(result)
        atipicos = _atipicos_para_decidir(result)
        result_final = result
        serie_final = serie_efectiva
        decisiones_chow: list[dict] = []
        rechazados: list[int] = []

        if atipicos:
            estado_chow = session_store.get_session(session_id)
            if estado_chow is not None:
                estado_chow.atipicos_pendientes = atipicos
            yield _sse(
                "outlier_detected",
                {
                    "session_id": session_id,
                    "atipicos": atipicos,
                    # El más extremo, por compatibilidad con clientes viejos.
                    "valor_atipico": valor_atipico,
                },
            )

            recibio_decision = await session_store.wait_for_decision(session_id)

            if not recibio_decision:
                yield _sse(
                    "error",
                    {
                        "codigo": "SESSION_TIMEOUT",
                        "mensaje": "Tiempo de espera agotado para decisión del atípico.",
                    },
                )
                return

            # DECISIÓN 053 — decision es un dict desde acá, no un str: mismo
            # mecanismo que usará distribution-decision, cada consumidor lee
            # su propia clave.
            decision_payload = session_store.get_decision(session_id) or {}
            decision_por_indice = {
                d["indice"]: d["decision"]
                for d in decision_payload.get("decisiones", [])
            }
            decisiones_chow = [
                {
                    **a,
                    "decision": decision_por_indice[a["indice"]],
                    "codigo": "TEST_OUTLIER_REJECTED_BY_USER"
                    if decision_por_indice[a["indice"]] == "rechazar"
                    else "TEST_OUTLIER_ACCEPTED_BY_USER",
                }
                for a in atipicos
            ]
            rechazados = [
                _mapear_indice_a_serie_original(a["indice"], serie_efectiva)
                for a in decisiones_chow
                if a["decision"] == "rechazar"
            ]

            if rechazados:
                # DECISIÓN 079 — los rechazados se excluyen JUNTOS, con la misma
                # operación que la simulación de exclusión (DECISIÓN 071). La
                # serie y sus timestamps se filtran de a pares: sin eso todo
                # punto posterior quedaba corrido un año (hallazgo V2, plan
                # post-avance 14/08/2026).
                recortada = aplicar_exclusiones(
                    serie_efectiva,
                    timestamps_efectivos
                    if timestamps_efectivos is not None
                    else [None] * len(serie_efectiva),
                    rechazados,
                )
                serie_filtrada = recortada.serie
                timestamps_filtrados = (
                    None if timestamps_efectivos is None else recortada.anios
                )

                result_final = ejecutar_etapa1(
                    serie=serie_filtrada,
                    tipo_variable=tipo_variable,
                    # "anual" forzado, no parsed.resolucion_temporal — si era
                    # "mensual", serie_efectiva ya es la agregada, no
                    # corresponde volver a agregarla.
                    resolucion_temporal="anual",
                    timestamps=timestamps_filtrados,
                    cramer_particion=cramer_particion,
                    # Sin esto la segunda ejecución caía al default (7) aunque
                    # el usuario haya elegido otro mes (DECISIÓN 057) — mismo
                    # hallazgo V2.
                    mes_inicio_anio=mes_inicio_anio,
                    variable_diaria=variable_diaria,
                    # DECISIÓN 078 — el mismo α que la primera pasada: sin esto
                    # la segunda caía al 5 % por defecto, el mismo defecto que
                    # ya tuvo mes_inicio_anio.
                    alfa=alfa,
                )
                # PR 3 (DECISIÓN 058) — esta segunda ejecución corre sobre
                # serie_filtrada (ya agregada), así que no tiene forma de
                # conocer la serie mensual cruda original: sus propios
                # serie_original/timestamps_originales/resolucion_original
                # quedarían iguales a la entrada de ESTA llamada, no a la
                # subida real del usuario. `result` (la primera ejecución,
                # antes de que Chow pausara) es la única que los conoce de
                # verdad — se copian acá para que el resultado final (el que
                # se serializa y persiste) siga exponiendo el origen real.
                result_final.serie_original = result.serie_original
                result_final.timestamps_originales = result.timestamps_originales
                result_final.resolucion_original = result.resolucion_original
                # PR 2.5 — la segunda ejecución fuerza resolucion_temporal="anual",
                # así que NO re-emite los warnings del paso 0 (recorte de
                # extremos, hueco interior, serie diaria). Esos describen el
                # archivo subido, no esta pasada: se arrastran desde la
                # primera ejecución, igual que serie_original. Sin esto,
                # rechazar un atípico borraba CONTRACT_PARTIAL_YEARS_TRIMMED /
                # CONTRACT_DAILY_SERIES_AGGREGATED del resultado final.
                warnings_agregacion_previos = [
                    w for w in result.warnings if w.codigo in CODIGOS_WARNING_AGREGACION
                ]
                result_final.warnings = warnings_agregacion_previos + [
                    w
                    for w in result_final.warnings
                    if w.codigo not in CODIGOS_WARNING_AGREGACION
                ]
                serie_final = serie_filtrada

                for evento in _emitir_resultado(result_final, iteracion=2):
                    yield evento

        if decisiones_chow:
            _describir_chow_tras_decision(
                result_final, decisiones_chow, bool(rechazados)
            )

        # Emitir resultado final completo
        yield _sse("result_etapa1", _serializar_etapa1(result_final, mes_inicio_anio))

        # Etapa 2 — DECISIÓN 052/055. Solo si el usuario la pidió y Etapa 1
        # no fue rechazada; RF-GEN-P-03: ningún nivel de warning bloquea,
        # solo nivel_confianza == "rechazado" lo hace. Corre sobre
        # serie_final — la misma población sobre la que se calculó el
        # veredicto final de Etapa 1 (post-Chow si el atípico se rechazó).
        etapa2_result: Etapa2Result | None = None
        decision_etapa2: dict | None = None
        # Bloque C2a (plan post-avance) — la elección + sus resultados, para
        # persistir junto al ranking. Se arma junto con result_etapa2_eventos
        # más abajo (misma data, evita recalcular).
        seleccion_etapa2: dict | None = None

        if 2 in etapas and result_final.nivel_confianza != "rechazado":
            valores_numericos = filtrar_numericos(serie_final)
            serie_np = np.asarray(valores_numericos, dtype=float)
            tiene_ceros = bool(np.any(serie_np == 0))
            tiene_negativos = bool(np.any(serie_np < 0))  # DECISIÓN 073

            yield _sse(
                "progress",
                {
                    "paso": "ajuste_distribuciones",
                    "etapa": 2,
                    "completado": 1,
                    "total": 1,
                },
            )

            etapa2_result = ejecutar_etapa2(
                serie_np, tiene_ceros=tiene_ceros, tiene_negativos=tiene_negativos
            )

            # Guardar en la sesión antes de pausar — distribution-decision
            # necesita estos parámetros ya ajustados, no reajustar las 13
            # distribuciones de nuevo (DECISIÓN 053).
            estado_sesion = session_store.get_session(session_id)
            if estado_sesion is not None:
                estado_sesion.serie = valores_numericos
                estado_sesion.tiene_ceros = tiene_ceros
                estado_sesion.tiene_negativos = tiene_negativos
                estado_sesion.etapa2 = etapa2_result
                # El mismo asyncio.Event pudo haberse usado ya para la
                # pausa de Chow arriba — un Event no se "des-setea" solo,
                # así que sin este clear() la segunda espera devolvería
                # True al instante, sin esperar la decisión real.
                estado_sesion.event.clear()

            yield _sse(
                "result_etapa2_ranking",
                {"session_id": session_id, **_serializar_etapa2(etapa2_result)},
            )

            recibio_decision_etapa2 = await session_store.wait_for_decision(session_id)

            if not recibio_decision_etapa2:
                yield _sse(
                    "error",
                    {
                        "codigo": "SESSION_TIMEOUT",
                        "mensaje": "Tiempo de espera agotado para la selección de distribución.",
                    },
                )
                return

            decision_etapa2 = session_store.get_decision(session_id)
            distribucion_elegida = decision_etapa2["distribucion"]
            metodo_elegido = decision_etapa2["metodo"]
            periodos_retorno = decision_etapa2["periodos_retorno"]

            dist_result = next(
                (
                    d
                    for d in etapa2_result.ranking
                    if d.distribucion == distribucion_elegida
                ),
                None,
            )
            metodo_result = None
            if dist_result is not None:
                metodo_result = next(
                    (m for m in dist_result.metodos if m.metodo == metodo_elegido),
                    None,
                )

            if metodo_result is not None and metodo_result.parametros is not None:
                modulo = _MODULOS_POR_DISTRIBUCION[distribucion_elegida]
                eventos = calcular_eventos_diseno(
                    modulo, metodo_result.parametros, periodos_retorno
                )
                # Bloque C — curva continua de la distribución ajustada,
                # para el gráfico de ajuste (empíricos vs. curva).
                max_t_empirico = max(
                    (p.periodo_retorno for p in etapa2_result.puntos_empiricos),
                    default=1.05,
                )
                curva_ajuste = _calcular_curva_ajuste(
                    modulo, metodo_result.parametros, periodos_retorno, max_t_empirico
                )
            else:
                # Selección sin parámetros ajustados (status != "ok", o un
                # nombre que no matchea ninguna fila del ranking) — no se
                # puede calcular ningún evento, pero el request no se
                # rechaza acá: esa validación de forma ya pasó en
                # distribution-decision. Mismo principio que rige Etapa 2
                # completa: ningún caso especial detiene el pipeline.
                eventos = [
                    EventoDiseno(periodo_retorno=t, valor=None)
                    for t in periodos_retorno
                ]
                curva_ajuste = []

            eventos_diseno_dicts = [
                {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
                for e in eventos
            ]
            curva_ajuste_dicts = [
                {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
                for e in curva_ajuste
            ]
            yield _sse(
                "result_etapa2_eventos",
                {
                    "distribucion": distribucion_elegida,
                    "metodo": metodo_elegido,
                    "eventos_diseno": eventos_diseno_dicts,
                    "curva_ajuste": curva_ajuste_dicts,
                },
            )
            seleccion_etapa2 = {
                "distribucion": distribucion_elegida,
                "metodo": metodo_elegido,
                "periodos_retorno": periodos_retorno,
                "eventos_diseno": eventos_diseno_dicts,
                "curva_ajuste": curva_ajuste_dicts,
            }

        # Construir registro de decisiones. DECISIÓN 079: un registro por
        # atípico, con su código de auditoría. El historial y el PDF siguen
        # leyendo la forma vieja ({accion, dato}) de los análisis anteriores.
        decisiones: dict = {}
        if decisiones_chow:
            decisiones["chow"] = {"atipicos": decisiones_chow}
        if decision_etapa2 is not None:
            decisiones["distribucion"] = decision_etapa2

        # Persistir si es CU-01
        if user_id is not None:
            analysis_id = await _persistir(
                user_id=user_id,
                serie=serie_original,
                timestamps=parsed.timestamps,
                tipo_variable=tipo_variable,
                modo=modo,
                cramer_particion=cramer_particion,
                mes_inicio_anio=mes_inicio_anio,
                variable_diaria=variable_diaria,
                alfa=alfa,
                etapas=etapas,
                result=result_final,
                etapa2_result=etapa2_result,
                seleccion_etapa2=seleccion_etapa2,
                decisiones=decisiones,
                db=db,
                filename=filename,
            )

        yield _sse(
            "complete", {"analysis_id": str(analysis_id) if analysis_id else None}
        )

    finally:
        session_store.remove_session(session_id)


async def _persistir(
    user_id: uuid.UUID,
    serie: list[float],
    timestamps: list | None,
    tipo_variable: str,
    modo: str,
    cramer_particion: dict | str,
    mes_inicio_anio: int,
    variable_diaria: str,
    etapas: list[int],
    result: Etapa1Result,
    etapa2_result: Etapa2Result | None,
    seleccion_etapa2: dict | None,
    decisiones: dict,
    db: AsyncSession,
    filename: str,
    alfa: float = ALFA_DEFECTO,
) -> uuid.UUID:
    analysis = Analysis(
        user_id=user_id,
        serie=serie,
        # PR 3 (DECISIÓN 058 §1) — timestamps de la serie tal como se
        # subió, nunca agregados (a diferencia de datos.timestamps_efectivos
        # del resultado, que sí puede traer año-etiqueta). Normalizado a
        # ISO-8601 igual que timestamps_originales en _serializar_etapa1() —
        # el driver JSONB no sabe serializar pd.Timestamp crudo.
        timestamps=_serializar_timestamps(timestamps, agregados=False),
        tipo_variable=tipo_variable,
        etapas=[str(e) for e in etapas],
        modo=modo,
        # mes_inicio_anio (Bloque F3) no es opcional acá — dos análisis
        # sobre el mismo archivo con meses distintos dan series y
        # resultados distintos; sin guardarlo, el historial de CU-01
        # muestra un resultado que no se puede volver a producir.
        # nombre_archivo (F7a, plan de fixes pre-reunión) — sin columna
        # propia a propósito: analyses no la tiene y agregarla es una
        # migración que este fix no amerita (DECISIÓN, ver PR). Vive en
        # configuracion (JSONB, ya existe) igual que cramer_particion y
        # mes_inicio_anio.
        # variable_diaria (PR 2.5, R0.2) — mismo criterio que mes_inicio_anio:
        # dos análisis del mismo archivo diario declarado como "pico" vs.
        # "media" no dan resultados distintos hoy (el max() es el mismo),
        # pero sí un warning distinto y una interpretación distinta de los
        # eventos de diseño — el historial tiene que registrar cuál se
        # eligió. Se guarda siempre, aunque la resolución no sea diaria.
        configuracion={
            "cramer_particion": cramer_particion,
            "mes_inicio_anio": mes_inicio_anio,
            "variable_diaria": variable_diaria,
            "nombre_archivo": filename,
            # DECISIÓN 078 — mismo criterio: con otro α cambian los veredictos.
            "alfa": alfa,
        },
    )
    db.add(analysis)
    await db.flush()  # genera analysis.id sin cerrar la transacción

    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1=_serializar_etapa1(result, mes_inicio_anio),
        etapa2=(
            _serializar_etapa2(etapa2_result, seleccion_etapa2)
            if etapa2_result is not None
            else None
        ),
        decisiones=decisiones,
    )
    db.add(analysis_result)
    await db.commit()

    return analysis.id


async def registrar_outlier_decision(
    session_id: str,
    decisiones: list[dict],
    db: AsyncSession,
) -> dict | None:
    """Registra una decisión por atípico y desbloquea el stream (DECISIÓN 079).

    None si la sesión no existe (el borde responde 404 SESSION_NOT_FOUND).
    Levanta DecisionAtipicoInvalidaError si los índices no son exactamente los
    de la pausa: decidir uno de menos, uno ajeno o uno dos veces no puede
    desbloquear el stream con un resultado a medias.
    """
    estado = session_store.get_session(session_id)
    if estado is None:
        return None
    pendientes = {a["indice"] for a in estado.atipicos_pendientes or []}
    indices = [d["indice"] for d in decisiones]
    if (
        not pendientes
        or len(indices) != len(set(indices))
        or set(indices) != pendientes
    ):
        raise DecisionAtipicoInvalidaError(
            "Hay que decidir exactamente los atípicos detectados, una vez cada uno: "
            f"{sorted(pendientes)}."
        )
    # DECISIÓN 053 — resolve_session recibe un dict.
    session_store.resolve_session(session_id, {"decisiones": decisiones})
    return {"ok": True, "pipeline_continua": True}


async def registrar_distribution_decision(
    session_id: str,
    distribucion: str,
    metodo: str,
    periodos_retorno: list[float],
) -> dict | None:
    """Registra la selección de distribución+método y desbloquea el stream
    en espera (DECISIÓN 052).

    Retorna None si la sesión no existe — el borde del endpoint lo traduce
    a 404 SESSION_NOT_FOUND, igual que registrar_outlier_decision() desde la
    DECISIÓN 079.
    """
    if session_store.get_session(session_id) is None:
        return None
    session_store.resolve_session(
        session_id,
        {
            "distribucion": distribucion,
            "metodo": metodo,
            "periodos_retorno": periodos_retorno,
        },
    )
    return {"ok": True, "pipeline_continua": True}


async def get_analysis_by_id(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> dict | None:
    stmt = (
        select(Analysis, AnalysisResult)
        .join(AnalysisResult, AnalysisResult.analysis_id == Analysis.id)
        .where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        return None

    analysis, result = row
    return {
        "id": str(analysis.id),
        "tipo_variable": analysis.tipo_variable,
        "modo": analysis.modo,
        "etapas": analysis.etapas,
        "created_at": analysis.created_at.isoformat(),
        "etapa1": result.etapa1,
        "etapa2": result.etapa2,
        # C2b (plan post-avance) — registro de auditoría de CU-01: qué
        # decidió el usuario ante el atípico y ante la distribución
        # (analysis_results.decisiones ya se persistía, este endpoint nunca
        # lo devolvía). `{}` para análisis sin ninguna pausa resuelta —
        # nunca None, `_persistir()` siempre recibe al menos `{}`.
        "decisiones": result.decisiones,
        # PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058) —
        # cierra el hueco que dejó anotado el PR 9 del plan de Etapa 2: sin
        # `configuracion` acá, la nota de criterio de año de
        # Etapa1ResultView nunca llegaba a HistoryDetailPage aunque
        # mes_inicio_anio ya se persistía desde DECISIÓN 057. `serie`/
        # `timestamps` son la entrada cruda auditada (analyses), no el
        # resultado — ver DECISIÓN 058 §1 para la partición completa.
        "serie": analysis.serie,
        "timestamps": analysis.timestamps,
        "configuracion": _configuracion_con_alfa(analysis.configuracion),
    }


def _configuracion_con_alfa(configuracion: dict | None) -> dict:
    """DECISIÓN 078 — los análisis guardados antes de que α fuera configurable
    corrieron con 5 %, pero no lo registraron. Se devuelve `alfa = 0.05` con
    `alfa_implicito = True`: la interfaz y el PDF lo muestran como el valor por
    defecto de entonces, no como una elección del usuario. Sin backfill en la
    BD (mismo criterio que `timestamps`, DECISIÓN 058 §4)."""
    configuracion = dict(configuracion or {})
    if "alfa" not in configuracion:
        configuracion["alfa"] = ALFA_DEFECTO
        configuracion["alfa_implicito"] = True
    return configuracion


async def recalcular_eventos_diseno(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    distribucion: str,
    metodo: str,
    periodos_retorno: list[float],
    db: AsyncSession,
) -> dict | None:
    """Bloque C2c (plan post-avance) — recálculo stateless de eventos de
    diseño desde el historial, para explorar una distribución distinta de
    la elegida durante el stream sin reajustar nada: los `parametros` de
    las 28 combinaciones ya están en `analysis_results.etapa2.ranking`
    (DECISIÓN 055).

    No toca session_store (no hay stream en curso), no persiste nada y no
    altera `decisiones` — DECISIÓN 062, "explorar no es decidir".

    Retorna None si el análisis no existe, no pertenece al usuario, o no
    tiene Etapa 2 ejecutada (`etapa2` es `None`) — mismo guard de
    pertenencia que get_analysis_by_id(), el borde del endpoint lo traduce
    a 404 ANALYSIS_NOT_FOUND sin distinguir los tres casos entre sí.
    Levanta MetodoNoAjustadoError si la combinación pedida no aparece en el
    ranking o no tiene `parametros` (status != "ok") — 400
    DIST_METHOD_NOT_FITTED.
    """
    stmt = (
        select(Analysis, AnalysisResult)
        .join(AnalysisResult, AnalysisResult.analysis_id == Analysis.id)
        .where(Analysis.id == analysis_id, Analysis.user_id == user_id)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        return None

    _, result = row
    etapa2 = result.etapa2
    if etapa2 is None:
        return None

    dist_dict = next(
        (d for d in etapa2["ranking"] if d["distribucion"] == distribucion), None
    )
    metodo_dict = (
        next((m for m in dist_dict["metodos"] if m["metodo"] == metodo), None)
        if dist_dict is not None
        else None
    )
    if (
        metodo_dict is None
        or metodo_dict["status"] != "ok"
        or metodo_dict["parametros"] is None
    ):
        raise MetodoNoAjustadoError()

    modulo = _MODULOS_POR_DISTRIBUCION[distribucion]
    parametros = metodo_dict["parametros"]
    eventos = calcular_eventos_diseno(modulo, parametros, periodos_retorno)

    max_t_empirico = max(
        (p["periodo_retorno"] for p in etapa2.get("puntos_empiricos", [])),
        default=1.05,
    )
    curva_ajuste = _calcular_curva_ajuste(
        modulo, parametros, periodos_retorno, max_t_empirico
    )

    return {
        "eventos_diseno": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor} for e in eventos
        ],
        "curva_ajuste": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
            for e in curva_ajuste
        ],
    }


async def get_history(
    user_id: uuid.UUID,
    db: AsyncSession,
    incluir_archivados: bool = False,
) -> list[dict]:
    stmt = select(Analysis).where(Analysis.user_id == user_id)
    if not incluir_archivados:
        stmt = stmt.where(Analysis.archivado_at.is_(None))
    stmt = stmt.order_by(Analysis.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(a.id),
            "tipo_variable": a.tipo_variable,
            "modo": a.modo,
            "etapas": a.etapas,
            "created_at": a.created_at.isoformat(),
            "archivado_at": a.archivado_at.isoformat() if a.archivado_at else None,
            # F7a (plan de fixes pre-reunión) — null para cualquier análisis
            # persistido antes de este fix (sin backfill, mismo criterio que
            # `timestamps`/DECISIÓN 058 §4): configuracion no tenía esta
            # clave todavía. El frontend degrada a tipo_variable en ese caso.
            "nombre_archivo": (a.configuracion or {}).get("nombre_archivo"),
            # F7b — la serie completa ya vive en analyses.serie (~40 valores
            # típicos), así que reusarla acá no cambia el orden de magnitud
            # del payload de la lista. Sparkline decorativa, no un gráfico
            # real — sin timestamps, sin ejes.
            "serie_preview": a.serie,
            # DECISIÓN 078 — 0.05 para los análisis anteriores (sin backfill).
            "alfa": _configuracion_con_alfa(a.configuracion)["alfa"],
        }
        for a in rows
    ]


async def archive_analysis(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> bool:
    """Marca un análisis como archivado. Retorna False si no existe o no pertenece al usuario."""
    stmt = select(Analysis).where(
        Analysis.id == analysis_id, Analysis.user_id == user_id
    )
    analysis = (await db.execute(stmt)).scalar_one_or_none()
    if analysis is None:
        return False
    analysis.archivado_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    return True


async def unarchive_analysis(
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> bool:
    """Revierte el archivado de un análisis. Retorna False si no existe o no pertenece al usuario."""
    stmt = select(Analysis).where(
        Analysis.id == analysis_id, Analysis.user_id == user_id
    )
    analysis = (await db.execute(stmt)).scalar_one_or_none()
    if analysis is None:
        return False
    analysis.archivado_at = None
    await db.commit()
    return True


def _seleccion_recalculada(etapa2_result: Etapa2Result, seleccion: dict) -> dict:
    """Eventos de diseño y curva de ajuste de `seleccion` sobre un Etapa 2 ya
    recalculado (simulate-exclusion). Misma forma que `seleccion` en
    `analysis_results.etapa2`, y el mismo trato que el stream cuando la
    combinación no tiene parámetros: eventos en null, curva vacía."""
    distribucion = seleccion["distribucion"]
    metodo = seleccion["metodo"]
    periodos_retorno = seleccion["periodos_retorno"]

    dist_result = next(
        (d for d in etapa2_result.ranking if d.distribucion == distribucion), None
    )
    metodo_result = (
        next((m for m in dist_result.metodos if m.metodo == metodo), None)
        if dist_result is not None
        else None
    )

    if (
        metodo_result is not None
        and metodo_result.status == "ok"
        and metodo_result.parametros is not None
    ):
        modulo = _MODULOS_POR_DISTRIBUCION[distribucion]
        eventos = calcular_eventos_diseno(
            modulo, metodo_result.parametros, periodos_retorno
        )
        max_t_empirico = max(
            (p.periodo_retorno for p in etapa2_result.puntos_empiricos),
            default=1.05,
        )
        curva_ajuste = _calcular_curva_ajuste(
            modulo, metodo_result.parametros, periodos_retorno, max_t_empirico
        )
    else:
        eventos = [
            EventoDiseno(periodo_retorno=t, valor=None) for t in periodos_retorno
        ]
        curva_ajuste = []

    return {
        "distribucion": distribucion,
        "metodo": metodo,
        "periodos_retorno": periodos_retorno,
        "eventos_diseno": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor} for e in eventos
        ],
        "curva_ajuste": [
            {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
            for e in curva_ajuste
        ],
    }


def simular_exclusion(
    serie: list[float],
    anios: list[int],
    tipo_variable: str,
    cramer_particion: dict | str,
    indices_excluidos: list[int],
    etapas: list[int],
    tratamiento: str = "eliminar",
    seleccion: dict | None = None,
    alfa: float = ALFA_DEFECTO,
) -> dict:
    """POST /analysis/simulate-exclusion — DECISIÓN 071, ítem A del feedback de
    directores. Recalcula Etapa 1 (y Etapa 2 si se pidió) sobre `serie` sin los
    puntos de `indices_excluidos`.

    Mismo patrón que `recalcular_eventos_diseno()`: sin session_store, sin BD, no
    persiste nada ni toca `decisiones` (DECISIÓN 062, "explorar no es decidir").

    Corre la batería como la segunda pasada del rechazo de Chow: sobre una serie
    que ya está agregada (`resolucion_temporal="anual"`, no se vuelve a agregar), y
    con Chow sin pausa — un atípico nuevo se informa en `etapa1.atipicos`, no
    detiene nada. El flujo de Chow del stream no se toca: que los dos den lo mismo
    lo prueba un test de integración, no un refactor compartido.

    Con `seleccion` ({distribucion, metodo, periodos_retorno}, la elección del
    análisis original) y Etapa 2 recalculada, `etapa2.seleccion` trae los eventos
    de diseño y la curva de ajuste de esa misma elección con los parámetros
    reajustados sin los puntos excluidos — los gráficos de evento de diseño se
    comparan contra el original. Si la combinación ya no ajusta, los eventos van
    con `valor: null` y la curva vacía, igual que en el stream.

    Levanta `ExclusionInvalidaError` (core/pipeline/exclusiones.py) si el pedido no
    aplica a la serie — el borde lo traduce a 400 CONTRACT_EXCLUSION_INVALID.
    """
    recortada = aplicar_exclusiones(serie, anios, indices_excluidos, tratamiento)

    result = ejecutar_etapa1(
        serie=recortada.serie,
        tipo_variable=tipo_variable,
        resolucion_temporal="anual",
        timestamps=recortada.anios,
        cramer_particion=cramer_particion,
        alfa=alfa,
    )

    etapa2 = None
    if 2 in etapas and result.nivel_confianza != "rechazado":
        valores = np.asarray(filtrar_numericos(result.serie_efectiva), dtype=float)
        etapa2_result = ejecutar_etapa2(
            valores,
            tiene_ceros=bool(np.any(valores == 0)),
            tiene_negativos=bool(np.any(valores < 0)),
        )
        etapa2 = _serializar_etapa2(
            etapa2_result,
            seleccion=_seleccion_recalculada(etapa2_result, seleccion)
            if seleccion is not None
            else None,
        )

    return {
        # mes_inicio_anio no cambia nada con una serie ya anual: solo decide la
        # versión calendario, que se arma con carga mensual o diaria.
        "etapa1": _serializar_etapa1(result, mes_inicio_anio=7),
        "etapa2": etapa2,
        "excluidos": [
            {
                "indice": e.indice,
                "periodo": e.periodo,
                "valor_original": e.valor_original,
            }
            for e in recortada.excluidos
        ],
        "serie": recortada.serie,
        "anios": recortada.anios,
    }

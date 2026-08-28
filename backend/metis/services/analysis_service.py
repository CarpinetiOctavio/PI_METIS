import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metis.core.etapa2.design_events import calcular_eventos_diseno
from metis.core.etapa2.types import Etapa2Result, EventoDiseno
from metis.core.pipeline import ejecutar_etapa1, ejecutar_etapa2
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
    # R3.4 (docs/plan-resolucion-diaria.md) — `resolucion=` es OBLIGATORIO.
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
            # Bloque D (plan post-avance, DECISIÓN 064) — piezas para la
            # fórmula sustituida en modo paso a paso. None para pruebas
            # "no_ejecutada" (nada que sustituir).
            "explicacion": (
                {
                    "ecuacion": tr.explicacion.ecuacion,
                    "terminos": tr.explicacion.terminos,
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

    # R3.3 opción 2 (docs/plan-resolucion-diaria.md) — qué serie cruda viaja
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

        # Chow detectó atípico — pausar y esperar decisión (CU-01 y CU-02)
        valor_atipico = _extraer_atipico(result)
        result_final = result
        serie_final = serie_efectiva

        if valor_atipico is not None:
            yield _sse(
                "outlier_detected",
                {"session_id": session_id, "valor_atipico": valor_atipico},
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
            decision_payload = session_store.get_decision(session_id)
            decision = decision_payload["decision"] if decision_payload else None

            if decision == "rechazar":
                indice_atipico = _extraer_indice_atipico(result)
                indice_real = _mapear_indice_a_serie_original(
                    indice_atipico, serie_efectiva
                )
                serie_filtrada = serie_efectiva.copy()
                del serie_filtrada[indice_real]

                # timestamps_efectivos está alineado 1:1 con serie_efectiva
                # (misma construcción en ejecutar_etapa1()) — sin filtrar acá
                # con el mismo índice, quedaba un elemento más largo que
                # serie_filtrada: validar_contrato() evaluaba duplicados/orden/
                # espaciado contra timestamps que ya no correspondían a la
                # serie analizada, y todo punto posterior al atípico quedaba
                # corrido un año en los gráficos (serie temporal, Chow) del
                # resultado final. Hallazgo V2, plan post-avance 14/08/2026.
                timestamps_filtrados = (
                    None
                    if timestamps_efectivos is None
                    else [
                        t
                        for i, t in enumerate(timestamps_efectivos)
                        if i != indice_real
                    ]
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
                serie_final = serie_filtrada

                for evento in _emitir_resultado(result_final, iteracion=2):
                    yield evento

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

            yield _sse(
                "progress",
                {
                    "paso": "ajuste_distribuciones",
                    "etapa": 2,
                    "completado": 1,
                    "total": 1,
                },
            )

            etapa2_result = ejecutar_etapa2(serie_np, tiene_ceros=tiene_ceros)

            # Guardar en la sesión antes de pausar — distribution-decision
            # necesita estos parámetros ya ajustados, no reajustar las 13
            # distribuciones de nuevo (DECISIÓN 053).
            estado_sesion = session_store.get_session(session_id)
            if estado_sesion is not None:
                estado_sesion.serie = valores_numericos
                estado_sesion.tiene_ceros = tiene_ceros
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

        # Construir registro de decisiones
        decisiones: dict = {}
        if valor_atipico is not None:
            decisiones["chow"] = {
                "accion": decision,
                "dato": valor_atipico,
            }
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
    etapas: list[int],
    result: Etapa1Result,
    etapa2_result: Etapa2Result | None,
    seleccion_etapa2: dict | None,
    decisiones: dict,
    db: AsyncSession,
    filename: str,
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
        configuracion={
            "cramer_particion": cramer_particion,
            "mes_inicio_anio": mes_inicio_anio,
            "nombre_archivo": filename,
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
    decision: str,
    dato_atipico: float,
    db: AsyncSession,
) -> dict:
    # DECISIÓN 053 — resolve_session ahora recibe un dict, no un str.
    session_store.resolve_session(session_id, {"decision": decision})
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
    a 404 SESSION_NOT_FOUND. A diferencia de registrar_outlier_decision(),
    acá el chequeo de existencia es explícito porque el contrato de
    distribution-decision lo exige (DECISIÓN 052), no porque Chow tuviera
    el mismo gap resuelto — ese gap queda tal como está, fuera de alcance.
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
        "configuracion": analysis.configuracion,
    }


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
    analysis.archivado_at = datetime.utcnow()
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

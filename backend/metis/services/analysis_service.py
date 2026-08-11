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
from metis.core.validacion.parser import parse_file
from metis.db.models import Analysis, AnalysisResult
from metis.services import session_store

_MODULOS_POR_DISTRIBUCION = dict(_DISTRIBUCIONES)


def _sse(tipo: str, payload: dict) -> str:
    return f"event: {tipo}\ndata: {json.dumps(payload)}\n\n"


def _serializar_etapa1(result: Etapa1Result) -> dict:
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
        }

    def warning_dict(w) -> dict:
        return {"codigo": w.codigo, "nivel": w.nivel, "descripcion": w.descripcion}

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
    }


def _serializar_etapa2(result: Etapa2Result) -> dict:
    """Hermana exacta de _serializar_etapa1() (DECISIÓN 055, Bloque A5).

    Serializa la grilla completa — las 13 distribuciones con TODOS sus
    métodos, incluidos no_converge/no_aplicable/disabled_zeros. No aplana
    a un top-3: la tesis misma reporta que ciertas combinaciones no
    convergen, y eso es información docente, no un error a esconder.
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
    }


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
        )

        for evento in _emitir_resultado(result, iteracion=1):
            yield evento

        if result.contract.bloqueante:
            yield _sse("complete", {"analysis_id": None})
            return

        # Chow detectó atípico — pausar y esperar decisión (CU-01 y CU-02)
        valor_atipico = _extraer_atipico(result)
        result_final = result
        serie_final = serie_original

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
                    indice_atipico, serie_original
                )
                serie_filtrada = serie_original.copy()
                del serie_filtrada[indice_real]

                result_final = ejecutar_etapa1(
                    serie=serie_filtrada,
                    tipo_variable=tipo_variable,
                    resolucion_temporal=parsed.resolucion_temporal,
                    timestamps=parsed.timestamps,
                    cramer_particion=cramer_particion,
                )
                serie_final = serie_filtrada

                for evento in _emitir_resultado(result_final, iteracion=2):
                    yield evento

        # Emitir resultado final completo
        yield _sse("result_etapa1", _serializar_etapa1(result_final))

        # Etapa 2 — DECISIÓN 052/055. Solo si el usuario la pidió y Etapa 1
        # no fue rechazada; RF-GEN-P-03: ningún nivel de warning bloquea,
        # solo nivel_confianza == "rechazado" lo hace. Corre sobre
        # serie_final — la misma población sobre la que se calculó el
        # veredicto final de Etapa 1 (post-Chow si el atípico se rechazó).
        etapa2_result: Etapa2Result | None = None
        decision_etapa2: dict | None = None

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
                # para el gráfico de ajuste (empíricos vs. curva). No son
                # los eventos de diseño que pidió el usuario (T discretos,
                # ej. [2, 5, ..., 500]): es un muestreo denso en escala log
                # de T=1.05 hasta el mayor entre el T pedido y el T empírico
                # máximo de la muestra, para que la curva cubra el mismo
                # rango que los puntos empíricos.
                max_t_empirico = max(
                    (p.periodo_retorno for p in etapa2_result.puntos_empiricos),
                    default=1.05,
                )
                t_max_curva = max(max(periodos_retorno, default=1.05), max_t_empirico)
                periodos_curva = np.geomspace(
                    1.05, max(t_max_curva, 1.06), num=60
                ).tolist()
                curva_ajuste = calcular_eventos_diseno(
                    modulo, metodo_result.parametros, periodos_curva
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

            yield _sse(
                "result_etapa2_eventos",
                {
                    "distribucion": distribucion_elegida,
                    "metodo": metodo_elegido,
                    "eventos_diseno": [
                        {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
                        for e in eventos
                    ],
                    "curva_ajuste": [
                        {"periodo_retorno": e.periodo_retorno, "valor": e.valor}
                        for e in curva_ajuste
                    ],
                },
            )

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
                tipo_variable=tipo_variable,
                modo=modo,
                cramer_particion=cramer_particion,
                etapas=etapas,
                result=result_final,
                etapa2_result=etapa2_result,
                decisiones=decisiones,
                db=db,
            )

        yield _sse(
            "complete", {"analysis_id": str(analysis_id) if analysis_id else None}
        )

    finally:
        session_store.remove_session(session_id)


async def _persistir(
    user_id: uuid.UUID,
    serie: list[float],
    tipo_variable: str,
    modo: str,
    cramer_particion: dict | str,
    etapas: list[int],
    result: Etapa1Result,
    etapa2_result: Etapa2Result | None,
    decisiones: dict,
    db: AsyncSession,
) -> uuid.UUID:
    analysis = Analysis(
        user_id=user_id,
        serie=serie,
        tipo_variable=tipo_variable,
        etapas=[str(e) for e in etapas],
        modo=modo,
        configuracion={"cramer_particion": cramer_particion},
    )
    db.add(analysis)
    await db.flush()  # genera analysis.id sin cerrar la transacción

    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1=_serializar_etapa1(result),
        etapa2=_serializar_etapa2(etapa2_result) if etapa2_result is not None else None,
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

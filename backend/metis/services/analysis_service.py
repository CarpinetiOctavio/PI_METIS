import json
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from metis.core.pipeline import ejecutar_etapa1
from metis.core.types import Etapa1Result
from metis.core.utils import es_numerico
from metis.core.validacion.parser import parse_file
from metis.db.models import Analysis, AnalysisResult
from metis.services import session_store


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


async def stream_etapa1(
    content: bytes,
    filename: str,
    columna_x: str,
    columna_y: str,
    tipo_variable: str,
    modo: str,
    cramer_particion: dict | str,
    session_id: str,
    user_id: uuid.UUID | None,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
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

            decision = session_store.get_decision(session_id)

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

                for evento in _emitir_resultado(result_final, iteracion=2):
                    yield evento

        # Emitir resultado final completo
        yield _sse("result_etapa1", _serializar_etapa1(result_final))

        # Construir registro de decisiones
        decisiones: dict = {}
        if valor_atipico is not None:
            decisiones["chow"] = {
                "accion": decision,
                "dato": valor_atipico,
            }

        # Persistir si es CU-01
        if user_id is not None:
            analysis_id = await _persistir(
                user_id=user_id,
                serie=serie_original,
                tipo_variable=tipo_variable,
                modo=modo,
                cramer_particion=cramer_particion,
                result=result_final,
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
    result: Etapa1Result,
    decisiones: dict,
    db: AsyncSession,
) -> uuid.UUID:
    analysis = Analysis(
        user_id=user_id,
        serie=serie,
        tipo_variable=tipo_variable,
        etapas=["1"],
        modo=modo,
        configuracion={"cramer_particion": cramer_particion},
    )
    db.add(analysis)
    await db.flush()  # genera analysis.id sin cerrar la transacción

    analysis_result = AnalysisResult(
        analysis_id=analysis.id,
        etapa1=_serializar_etapa1(result),
        etapa2=None,
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
    session_store.resolve_session(session_id, decision)
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
) -> list[dict]:
    stmt = (
        select(Analysis)
        .where(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(a.id),
            "tipo_variable": a.tipo_variable,
            "modo": a.modo,
            "etapas": a.etapas,
            "created_at": a.created_at.isoformat(),
        }
        for a in rows
    ]

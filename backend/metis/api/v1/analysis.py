import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from metis.api.deps import get_current_user, get_db, get_optional_user
from metis.core.validacion.parser import leer_columnas_preview
from metis.db.models.user import User
from metis.schemas.analysis import (
    CramerParticionCustom,
    DesignEventsRecalcRequest,
    DesignEventsRecalcResponse,
    DistributionDecisionRequest,
    DistributionDecisionResponse,
    OutlierDecisionRequest,
    OutlierDecisionResponse,
    PreviewColumnsResponse,
)
from metis.services.analysis_service import (
    MetodoNoAjustadoError,
    get_analysis_by_id,
    recalcular_eventos_diseno,
    registrar_distribution_decision,
    registrar_outlier_decision,
)

# Alias — el módulo de servicios ahora se llama igual que la ruta de abajo
# (stream_analysis), que redefine el nombre en este mismo namespace apenas
# se declara. Importar sin alias haría que la ruta se llamara a sí misma
# (recursión infinita) en vez de al generador real de services/.
from metis.services.analysis_service import stream_analysis as ejecutar_stream_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])

_ETAPAS_VALIDAS: dict[str, list[int]] = {"1": [1], "1,2": [1, 2]}

_ETAPAS_INVALIDAS = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "CONTRACT_ETAPAS_INVALID",
            "mensaje": "etapas debe ser '1' o '1,2'.",
        }
    },
)


def _parsear_etapas(etapas: str) -> list[int]:
    """DECISIÓN 054 — parseo en el borde, core/ nunca ve el string crudo."""
    if etapas not in _ETAPAS_VALIDAS:
        raise _ETAPAS_INVALIDAS
    return _ETAPAS_VALIDAS[etapas]


_MES_INICIO_INVALIDO = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "CONTRACT_MES_INICIO_INVALID",
            "mensaje": "mes_inicio_anio debe estar entre 1 y 12.",
        }
    },
)


def _validar_mes_inicio(mes_inicio_anio: int) -> int:
    """DECISIÓN 057 (Bloque F3) — validado en el borde, mismo tratamiento
    que _parsear_etapas(): core/ nunca ve un valor fuera de [1..12]."""
    if not (1 <= mes_inicio_anio <= 12):
        raise _MES_INICIO_INVALIDO
    return mes_inicio_anio


def _cramer_particion_invalida(mensaje: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "error": {"codigo": "CONTRACT_CRAMER_PARTICION_INVALID", "mensaje": mensaje}
        },
    )


def _parsear_cramer_particion(raw: str) -> dict | str:
    """Bloque H1 (plan post-avance, DECISIÓN 036, opción 1) — 'default' pasa
    tal cual; cualquier otro valor se parsea como JSON y se valida como
    CramerParticionCustom. calcular_cramer() siempre supo recibir un dict
    (la rama `else` ya indexaba particion["n1_pct"]/["n2_pct"]) — el bug
    real era que nunca le llegaba uno, nunca que la rama estuviera mal.

    n1_pct > n2_pct se valida acá a mano (no con un Field de Pydantic
    comparando dos campos): el bloque 1 es el período largo y el 2 el
    corto — invertidos, Cramer no mide lo que dice medir. Que los bloques
    resultantes tengan al menos 2 datos depende de `n`, desconocido en este
    punto — esa validación vive en calcular_cramer() y produce
    no_ejecutada, no un 400 acá.
    """
    if raw == "default":
        return raw
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise _cramer_particion_invalida(
            "cramer_particion debe ser 'default' o un JSON con n1_pct y n2_pct."
        ) from None
    try:
        particion = CramerParticionCustom.model_validate(data)
    except ValidationError:
        raise _cramer_particion_invalida(
            "n1_pct y n2_pct deben ser números entre 1 y 100."
        ) from None
    if particion.n1_pct <= particion.n2_pct:
        raise _cramer_particion_invalida(
            "n1_pct debe ser mayor que n2_pct — el primer bloque es el período largo."
        )
    return {"n1_pct": particion.n1_pct, "n2_pct": particion.n2_pct}


# DECISIÓN 050 — mismo valor que client_max_body_size en nginx/nginx.conf y
# frontend/nginx.conf. nginx no es el único camino: :8000 está mapeado al
# host por diseño (architecture.md, "Exposición de puertos en desarrollo"),
# así que un cliente que salte el proxy tiene que encontrar el mismo límite acá.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024

_ARCHIVO_DEMASIADO_GRANDE = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "PARSE_FILE_TOO_LARGE",
            "mensaje": f"El archivo supera el límite de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        }
    },
)


async def _leer_archivo_limitado(archivo: UploadFile) -> bytes:
    """Lee un UploadFile en chunks, cortando apenas se supera MAX_UPLOAD_BYTES
    — nunca buferea un archivo entero por encima del límite en memoria, ni
    siquiera si el cliente miente el Content-Length (DECISIÓN 050)."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await archivo.read(_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise _ARCHIVO_DEMASIADO_GRANDE
        chunks.append(chunk)
    return b"".join(chunks)


@router.post("/preview-columns", response_model=PreviewColumnsResponse)
async def preview_columns(archivo: UploadFile = File(...)):
    # DECISIÓN 047 — stateless, sin dependencia de usuario: no hay ninguna
    # diferencia de comportamiento según quién llama, así que "JWT opcional"
    # se cumple por no inspeccionar la cookie en absoluto, no por leerla y
    # descartarla. No toca session_store ni BD.
    content = await _leer_archivo_limitado(archivo)
    try:
        columnas, filas = leer_columnas_preview(content, archivo.filename or "upload")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "codigo": "PARSE_ERROR",
                    "mensaje": "No se pudo leer el archivo. Verificá que sea un CSV o Excel válido.",
                }
            },
        ) from exc

    return PreviewColumnsResponse(columnas=columnas, filas=filas)


@router.post("/stream")
async def stream_analysis(
    archivo: UploadFile = File(...),
    columna_x: str = Form(...),
    columna_y: str = Form(...),
    tipo_variable: str = Form(...),
    etapas: str = Form("1"),
    modo: str = Form("experto"),
    cramer_particion: str = Form("default"),
    mes_inicio_anio: int = Form(7),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    # DECISIÓN 036 (Bloque H1, plan post-avance) — cramer_particion se
    # parsea y valida acá antes de que llegue a services/. Cierra el
    # TypeError que motivó la guarda anterior (CONTRACT_CRAMER_PARTICION_UNSUPPORTED,
    # ver api-contracts.md) implementando la opción 1 de verdad, no solo
    # bloqueando cualquier valor distinto de "default".
    cramer_particion_parseada = _parsear_cramer_particion(cramer_particion)

    etapas_parseadas = _parsear_etapas(etapas)
    mes_inicio_valido = _validar_mes_inicio(mes_inicio_anio)
    content = await _leer_archivo_limitado(archivo)
    session_id = str(uuid.uuid4())

    return StreamingResponse(
        ejecutar_stream_analysis(
            content=content,
            filename=archivo.filename or "upload",
            columna_x=columna_x,
            columna_y=columna_y,
            tipo_variable=tipo_variable,
            modo=modo,
            cramer_particion=cramer_particion_parseada,
            etapas=etapas_parseadas,
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            db=db,
            mes_inicio_anio=mes_inicio_valido,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/outlier-decision", response_model=OutlierDecisionResponse)
async def outlier_decision(
    body: OutlierDecisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    result = await registrar_outlier_decision(
        session_id=str(body.session_id),
        decision=body.decision,
        dato_atipico=body.dato_atipico,
        db=db,
    )
    return OutlierDecisionResponse(**result)


_DIST_SELECTION_INVALIDA = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "DIST_SELECTION_INVALID",
            "mensaje": "distribucion y metodo son obligatorios, y periodos_retorno"
            " debe tener entre 1 y 20 valores, todos mayores a 1.",
        }
    },
)

_SESSION_NOT_FOUND = HTTPException(
    status_code=404,
    detail={
        "error": {
            "codigo": "SESSION_NOT_FOUND",
            "mensaje": "La sesión no existe o ya expiró.",
        }
    },
)


def _validar_seleccion_distribucion(
    distribucion: str, metodo: str, periodos_retorno: list[float]
) -> None:
    """DECISIÓN 052 — validado en el borde, no con restricciones Pydantic:
    necesita responder 400 DIST_SELECTION_INVALID, no el 422 genérico que
    FastAPI dispararía solo. T > 1 porque F = 1 - 1/T necesita T > 1 para
    caer en (0,1) — mismo guard que cuantil() en core/, duplicado acá para
    devolver un error legible en vez de un 500. Compartida con
    /analysis/{id}/design-events (Bloque C2c) — la forma del request es la
    misma, el destino de la decisión es lo único que cambia."""
    if (
        not distribucion
        or not metodo
        or not (1 <= len(periodos_retorno) <= 20)
        or any(t <= 1 for t in periodos_retorno)
    ):
        raise _DIST_SELECTION_INVALIDA


@router.post("/distribution-decision", response_model=DistributionDecisionResponse)
async def distribution_decision(
    body: DistributionDecisionRequest,
    current_user: User | None = Depends(get_optional_user),
):
    _validar_seleccion_distribucion(
        body.distribucion, body.metodo, body.periodos_retorno
    )

    result = await registrar_distribution_decision(
        session_id=str(body.session_id),
        distribucion=body.distribucion,
        metodo=body.metodo,
        periodos_retorno=body.periodos_retorno,
    )
    if result is None:
        raise _SESSION_NOT_FOUND
    return DistributionDecisionResponse(**result)


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_analysis_by_id(
        analysis_id=analysis_id,
        user_id=current_user.id,
        db=db,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return result


_ANALYSIS_NOT_FOUND = HTTPException(
    status_code=404,
    detail={
        "error": {
            "codigo": "ANALYSIS_NOT_FOUND",
            "mensaje": "El análisis no existe, no pertenece al usuario, o no tiene Etapa 2 ejecutada.",
        }
    },
)

_DIST_METHOD_NOT_FITTED = HTTPException(
    status_code=400,
    detail={
        "error": {
            "codigo": "DIST_METHOD_NOT_FITTED",
            "mensaje": "Esa combinación de distribución y método no tiene parámetros ajustados.",
        }
    },
)


@router.post("/{analysis_id}/design-events", response_model=DesignEventsRecalcResponse)
async def recalcular_design_events(
    analysis_id: uuid.UUID,
    body: DesignEventsRecalcRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Bloque C2c (plan post-avance) — recálculo stateless desde el
    # historial. DECISIÓN 062: no toca session_store, no persiste nada, no
    # altera `decisiones`. Requiere JWT y pertenencia del análisis, mismo
    # guard que GET /history/{id}.
    _validar_seleccion_distribucion(
        body.distribucion, body.metodo, body.periodos_retorno
    )

    try:
        result = await recalcular_eventos_diseno(
            analysis_id=analysis_id,
            user_id=current_user.id,
            distribucion=body.distribucion,
            metodo=body.metodo,
            periodos_retorno=body.periodos_retorno,
            db=db,
        )
    except MetodoNoAjustadoError:
        raise _DIST_METHOD_NOT_FITTED from None

    if result is None:
        raise _ANALYSIS_NOT_FOUND
    return DesignEventsRecalcResponse(**result)

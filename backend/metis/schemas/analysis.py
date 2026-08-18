import uuid
from typing import Literal

from pydantic import BaseModel

# --- Tipos compartidos ---

TipoVariable = Literal["caudal_precipitacion", "otro"]
OutlierDecision = Literal["rechazar", "aceptar"]
Veredicto = Literal["aprobada", "rechazada"]
WarningNivel = Literal["critico", "normal"]

# DECISIÓN 054 — AnalysisRequest y CramerParticionCustom se borraron: el
# endpoint POST /analysis/stream es multipart/form-data con un UploadFile,
# que no modela bien con un BaseModel plano. Los Form(...) sueltos que ya
# declara api/v1/analysis.py son el modelo real; mantener un modelo Pydantic
# paralelo que ninguna ruta importaba era código muerto que afirmaba una
# validación tipada que nunca corría en runtime — ver DECISIÓN 037.


# --- Request/Response: POST /analysis/outlier-decision ---


class OutlierDecisionRequest(BaseModel):
    session_id: uuid.UUID
    decision: OutlierDecision
    dato_atipico: float


class OutlierDecisionResponse(BaseModel):
    ok: bool
    pipeline_continua: bool


# --- Request/Response: POST /analysis/distribution-decision (DECISIÓN 052) ---
# Reemplaza al design-events documentado en api-contracts.md y nunca
# implementado — los eventos de diseño viajan por el stream SSE, esto es
# solo la decisión que lo desbloquea. Sin restricciones de rango a nivel
# Pydantic (periodos_retorno > 1, máximo 20, etc.): esa validación produce
# 400 DIST_SELECTION_INVALID, no un 422 genérico de FastAPI, así que se
# hace a mano en el borde del endpoint, igual que cramer_particion.


class DistributionDecisionRequest(BaseModel):
    session_id: uuid.UUID
    distribucion: str
    metodo: str
    periodos_retorno: list[float]


class DistributionDecisionResponse(BaseModel):
    ok: bool
    pipeline_continua: bool


# --- Request/Response: POST /analysis/{id}/design-events (Bloque C2c, plan
# post-avance) — recálculo stateless de eventos de diseño desde el
# historial. No toca session_store, no persiste nada, no altera
# `decisiones` (DECISIÓN 062 — explorar no es decidir). Misma falta de
# restricciones Pydantic sobre periodos_retorno que DistributionDecisionRequest,
# por el mismo motivo: la validación de rango produce 400 DIST_SELECTION_INVALID
# a mano en el borde, no un 422 genérico.


class DesignEventsRecalcRequest(BaseModel):
    distribucion: str
    metodo: str
    periodos_retorno: list[float]


class EventoDisenoItem(BaseModel):
    periodo_retorno: float
    valor: float | None


class DesignEventsRecalcResponse(BaseModel):
    eventos_diseno: list[EventoDisenoItem]
    curva_ajuste: list[EventoDisenoItem]


# --- Response: POST /analysis/preview-columns (DECISIÓN 047) ---


class ColumnaPreview(BaseModel):
    nombre: str
    indice: int
    muestra: list[str]


class PreviewColumnsResponse(BaseModel):
    columnas: list[ColumnaPreview]
    filas: int


# --- Payloads de eventos SSE ---


class ProgressEvent(BaseModel):
    paso: str
    etapa: int
    completado: int
    total: int


class TestResultEvent(BaseModel):
    prueba: str
    estadistico: float | None
    valor_critico: float | None
    veredicto: Veredicto | None
    warning_codigo: str | None = None
    warning_nivel: WarningNivel | None = None
    n1: int | None = None
    n2: int | None = None


class ContractProblem(BaseModel):
    campo: str
    codigo: str
    descripcion: str
    accion: Literal["bloqueante", "continua"]


class WarningItem(BaseModel):
    codigo: str
    nivel: WarningNivel
    descripcion: str

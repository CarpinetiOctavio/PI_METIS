import uuid
from typing import Literal

from pydantic import BaseModel

# --- Tipos compartidos ---

TipoVariable = Literal["caudal_precipitacion", "otro"]
Etapa = Literal[1, 2]
OutlierDecision = Literal["rechazar", "aceptar"]
Veredicto = Literal["aprobada", "rechazada"]
WarningNivel = Literal["critico", "normal"]


# --- Request: POST /analysis/stream ---


class CramerParticionCustom(BaseModel):
    n1_pct: int
    n2_pct: int


class AnalysisRequest(BaseModel):
    columna_x: str
    columna_y: str
    tipo_variable: TipoVariable
    etapas: list[Etapa] = [1]
    modo: Literal["paso_a_paso", "experto"] = "experto"
    cramer_particion: Literal["default"] | CramerParticionCustom = "default"


# --- Request/Response: POST /analysis/outlier-decision ---


class OutlierDecisionRequest(BaseModel):
    session_id: uuid.UUID
    decision: OutlierDecision
    dato_atipico: float


class OutlierDecisionResponse(BaseModel):
    ok: bool
    pipeline_continua: bool


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

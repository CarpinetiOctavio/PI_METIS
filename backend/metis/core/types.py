from dataclasses import dataclass, field


@dataclass
class WarningItem:
    codigo: str
    nivel: str  # "critico" | "normal"
    descripcion: str


@dataclass
class TestResult:
    prueba: str
    estadistico: float | None
    valor_critico: float | None
    veredicto: str | None  # "aprobada" | "rechazada" | "no_ejecutada"
    warning_codigo: str | None = None
    warning_nivel: str | None = None  # "critico" | "normal"
    n1: int | None = None
    n2: int | None = None
    valor_atipico: float | None = None


@dataclass
class ContractResult:
    bloqueante: bool
    codigo_error: str | None
    warnings: list[WarningItem] = field(default_factory=list)


@dataclass
class DescriptiveStats:
    n: int
    media: float
    mediana: float
    desvio_estandar: float
    coef_variacion: float
    coef_asimetria: float
    minimo: float
    maximo: float


@dataclass
class Etapa1Result:
    contract: ContractResult
    descriptive: DescriptiveStats | None
    independencia: list[TestResult]
    homogeneidad: list[TestResult]
    tendencia: list[TestResult]
    atipicos: list[TestResult]
    nivel_independencia: str | None  # "independiente" | "dependiente"
    nivel_homogeneidad: (
        str | None
    )  # "homogeneidad_ok" | "homogeneidad_warning" | "homogeneidad_critica"
    nivel_confianza: str  # "validado" | "con_warnings" | "rechazado"
    warnings: list[WarningItem] = field(default_factory=list)


@dataclass
class ParsedData:
    serie: list[float]
    timestamps: list | None
    resolucion_temporal: str | None  # "anual" | "mensual" | None

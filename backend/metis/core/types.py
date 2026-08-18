from dataclasses import dataclass, field


@dataclass
class WarningItem:
    codigo: str
    nivel: str  # "critico" | "normal"
    descripcion: str


@dataclass
class Explicacion:
    """Piezas para reconstruir, en modo paso a paso, la fórmula con los
    valores de ESTA serie ya sustituidos — Bloque D del plan post-avance,
    DECISIÓN 064. `core/` calcula y expone los términos intermedios que la
    prueba ya usó de todos modos; el frontend solo renderiza (sustituye en
    una plantilla) e interpreta en lenguaje natural — nunca recalcula
    estadística. `ecuacion` referencia la ecuación de
    `.claude/rules/core/formulas-etapa1.md` (ej. "III-8"), nunca se
    implementa un término nuevo sin esa referencia, misma regla que rige
    cualquier fórmula del proyecto."""

    ecuacion: str
    terminos: dict[str, float | int | None]


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
    indice_atipico: int | None = None
    explicacion: Explicacion | None = None


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
    desvio_estandar: float  # Ec. IV-8, ddof=1
    coef_variacion: float  # Ec. IV-9
    coef_asimetria: float  # Ec. IV-5, no sesgada
    minimo: float
    maximo: float
    rango: float | None = None  # máximo - mínimo — tesis IV.5.1, RF-GEN-P-04
    varianza_sesgada: float | None = None  # Ec. IV-2
    varianza_no_sesgada: float | None = None  # Ec. IV-3
    asimetria_sesgada: float | None = None  # Ec. IV-4
    curtosis_sesgada: float | None = None  # Ec. IV-6
    curtosis_no_sesgada: float | None = None  # Ec. IV-7
    suma_log: float | None = None  # Σln(xi) — None si algún xi ≤ 0
    mpp_m0: float | None = None  # Ec. IV-21
    mpp_m1: float | None = None  # Ec. IV-22
    mpp_m2: float | None = None  # Ec. IV-23
    mpp_m3: float | None = None  # Ec. IV-24


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
    # Bloque F4 (agregación temporal) — la serie y los timestamps sobre los
    # que realmente corrió la batería estadística: iguales a los de entrada
    # si resolucion_temporal era "anual" (nada que agregar); la serie de
    # máximos anuales y sus año-etiqueta si era "mensual". services/ usa
    # esto (no la serie cruda de entrada) para todo lo que pasa DESPUÉS de
    # Etapa 1 — mapeo de índice de Chow, Etapa 2 — porque una vez agregada,
    # el resto del pipeline razona en el dominio anual, no en el mensual
    # crudo. `analyses.serie` en la persistencia sigue siendo la serie
    # cruda subida por el usuario — es otro campo, con otro propósito
    # (auditoría de lo que se subió, no de lo que se analizó).
    serie_efectiva: list[float] = field(default_factory=list)
    timestamps_efectivos: list | None = None
    # PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058) — la
    # serie tal como llegó a ejecutar_etapa1(), antes de cualquier
    # agregación: auditoría de la entrada, no del resultado. Igual a
    # serie_efectiva/timestamps_efectivos cuando no hubo agregación (la
    # serialización en services/ solo emite estos dos por separado cuando
    # resolucion_original == "mensual" — con carga anual duplicarlos es
    # peso muerto). resolucion_original conserva el valor de
    # resolucion_temporal tal como llegó, ANTES de que el paso 0 lo fuerce
    # a "anual" tras agregar.
    serie_original: list = field(default_factory=list)
    timestamps_originales: list | None = None
    resolucion_original: str | None = None


@dataclass
class ParsedData:
    serie: list[float]
    timestamps: list | None
    resolucion_temporal: str | None  # "anual" | "mensual" | None

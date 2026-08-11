from __future__ import annotations

from dataclasses import dataclass, field

from metis.core.types import WarningItem

CONVERGENCIA: float = 1e-7  # criterio fijo para métodos iterativos — no configurable

# Status de cada ajuste distribución+método
STATUS_OK = "ok"
STATUS_NO_CONVERGE = "no_converge"
STATUS_NO_APLICABLE = "no_aplicable"
STATUS_DISABLED_ZEROS = "disabled_zeros"


@dataclass
class MetodoResult:
    metodo: str  # "momentos" | "mv" | "ml" | "mpp" | "me" | "mc"
    parametros: dict | None  # None si el ajuste falló
    eea: float | None  # None si el ajuste falló
    status: str  # STATUS_* constants


@dataclass
class DistResult:
    distribucion: str
    n_parametros: int  # criterio de desempate: menor gana
    metodos: list[MetodoResult] = field(default_factory=list)
    mejor_eea: float | None = None  # EEA del mejor método; None si todos fallaron
    mejor_metodo: str | None = None


@dataclass
class EventoDiseno:
    periodo_retorno: float
    # None si cuantil() falló para este período de retorno puntual — un T
    # inválido para una distribución no puede tumbar el cálculo completo de
    # eventos de diseño (core/etapa2/design_events.py).
    valor: float | None


@dataclass
class PuntoEmpirico:
    """Posición de ploteo Weibull de un dato observado (empirical.py::probabilidades_weibull).

    Independiente de qué distribución se elija — es una propiedad de la
    muestra, no del ajuste. Bloque C del plan de Etapa 2: insumo del
    gráfico de ajuste (puntos empíricos vs. curva de la distribución).
    """

    valor: float
    periodo_retorno: float
    probabilidad: float


@dataclass
class Etapa2Result:
    # Ordenado por mejor_eea ASC; empate desempatado por n_parametros ASC
    ranking: list[DistResult]
    warnings: list[WarningItem] = field(default_factory=list)
    puntos_empiricos: list[PuntoEmpirico] = field(default_factory=list)

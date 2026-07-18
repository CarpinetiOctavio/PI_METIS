from dataclasses import dataclass

from metis.core.etapa2.types import Etapa2Result
from metis.core.types import Etapa1Result


@dataclass
class FullPipelineResult:
    etapa1: Etapa1Result
    etapa2: Etapa2Result | None  # None si Etapa 1 fue rechazada — Etapa 2 no corre

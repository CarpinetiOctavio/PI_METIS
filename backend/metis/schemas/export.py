from pydantic import BaseModel


class ExportSimulacionRequest(BaseModel):
    """POST /export/{id}/simulacion (DECISIÓN 075, addendum). Solo los índices:
    la serie, la configuración y la elección salen del análisis persistido. Son
    posiciones en `etapa1.datos.serie_efectiva`, igual que en
    POST /analysis/simulate-exclusion (DECISIÓN 071)."""

    indices_excluidos: list[int]

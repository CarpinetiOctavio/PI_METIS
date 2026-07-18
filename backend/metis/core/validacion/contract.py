import numpy as np

from metis.core.types import ContractResult, WarningItem
from metis.core.utils import es_numerico


def validar_contrato(
    serie: list,
    tipo_variable: str,
    resolucion_temporal: str | None = None,
    timestamps: list | None = None,
) -> ContractResult:
    warnings: list[WarningItem] = []

    # --- BLOQUEANTES ---

    valores_numericos = [v for v in serie if es_numerico(v)]

    if len(valores_numericos) < 10:
        return ContractResult(
            bloqueante=True,
            codigo_error="CONTRACT_SERIES_TOO_SHORT",
            warnings=[],
        )

    if resolucion_temporal is None:
        return ContractResult(
            bloqueante=True,
            codigo_error="CONTRACT_NO_TEMPORAL_RESOLUTION",
            warnings=[],
        )

    # --- NO BLOQUEANTES ---

    if len(valores_numericos) < 30:
        warnings.append(
            WarningItem(
                codigo="CONTRACT_LENGTH_WARNING",
                nivel="normal",
                descripcion=f"Serie con {len(valores_numericos)} datos — resultados no certificables",
            )
        )

    no_numericos = [v for v in serie if not es_numerico(v)]
    if no_numericos:
        warnings.append(
            WarningItem(
                codigo="CONTRACT_NON_NUMERIC_VALUES",
                nivel="normal",
                descripcion=f"{len(no_numericos)} valor(es) no numérico(s) detectado(s)",
            )
        )

    faltantes = [
        v for v in serie if v is None or (isinstance(v, float) and np.isnan(v))
    ]
    if faltantes:
        warnings.append(
            WarningItem(
                codigo="CONTRACT_MISSING_VALUES",
                nivel="normal",
                descripcion=f"{len(faltantes)} valor(es) faltante(s) o celda(s) vacía(s)",
            )
        )

    if tipo_variable == "caudal_precipitacion":
        negativos = [v for v in valores_numericos if v < 0]
        if negativos:
            warnings.append(
                WarningItem(
                    codigo="CONTRACT_NEGATIVE_VALUES",
                    nivel="normal",
                    descripcion=f"{len(negativos)} valor(es) negativo(s) en serie de caudal/precipitación",
                )
            )

    if timestamps is not None:
        if len(timestamps) != len(set(timestamps)):
            warnings.append(
                WarningItem(
                    codigo="CONTRACT_DUPLICATE_TIMESTAMPS",
                    nivel="normal",
                    descripcion="Duplicados temporales detectados en la serie",
                )
            )

        if timestamps != sorted(timestamps):
            warnings.append(
                WarningItem(
                    codigo="CONTRACT_WRONG_ORDER",
                    nivel="normal",
                    descripcion="La serie no está en orden cronológico",
                )
            )

        if not _espaciado_regular(timestamps):
            warnings.append(
                WarningItem(
                    codigo="CONTRACT_IRREGULAR_SPACING",
                    nivel="normal",
                    descripcion="Espaciado temporal irregular detectado",
                )
            )

    return ContractResult(bloqueante=False, codigo_error=None, warnings=warnings)


def _espaciado_regular(timestamps: list) -> bool:
    if len(timestamps) < 2:
        return True
    try:
        diffs = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        return len(set(diffs)) == 1
    except TypeError:
        return True

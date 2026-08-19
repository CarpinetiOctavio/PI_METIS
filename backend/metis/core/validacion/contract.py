import numpy as np

from metis.core.types import ContractResult, WarningItem
from metis.core.utils import es_numerico
from metis.core.validacion.parser import parsear_timestamps


def timestamps_desordenados(timestamps: list) -> bool:
    """True si `timestamps` NO está en orden cronológico ascendente (no
    estrictamente — duplicados adyacentes no cuentan como desorden, eso lo
    cubre CONTRACT_DUPLICATE_TIMESTAMPS aparte).

    Bloque H3 (plan post-avance, DECISIÓN 030) — comparación directa con
    `<` (vía `sorted()`), sin pasar por `parsear_timestamps()`: funciona
    igual para años enteros y para fechas ISO-8601 de texto (la
    comparación lexicográfica de fechas de ancho fijo coincide con el
    orden cronológico). Es la ARITMÉTICA de fechas de texto la que falla
    (ver `_espaciado_regular()` más abajo), no la comparación con `<`.

    Si el tipo no es comparable entre sí (una mezcla real no debería
    pasar en la práctica — una sola columna parseada por el parser es
    homogénea) no se puede determinar el orden con certeza: se trata como
    "en orden" en vez de bloquear un caso que no se puede evaluar.
    """
    try:
        return list(timestamps) != sorted(timestamps)
    except TypeError:
        return False


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

        # CONTRACT_WRONG_ORDER se movió a un chequeo bloqueante en
        # ejecutar_etapa1(), ANTES del paso 0 (agregación) — Bloque H3
        # (plan post-avance, DECISIÓN 030). Ya no vive acá por dos motivos:
        # (1) pasa de warning a error bloqueante, un tratamiento que esta
        # función no le da a nada más que no sea n<10/sin resolución
        # temporal (esos si están acá, como early-return, no como warning
        # de esta lista); (2) para que sirva de algo tiene que evaluar los
        # timestamps CRUDOS, antes de agregar — si corriera acá (después
        # de agregar_a_maximos_anuales(), que construye timestamps
        # siempre ascendentes por range()) sería código muerto para
        # cualquier serie mensual, exactamente el hallazgo que motivó
        # este bloque.

        if not _espaciado_regular(timestamps, resolucion_temporal):
            warnings.append(
                WarningItem(
                    codigo="CONTRACT_IRREGULAR_SPACING",
                    nivel="normal",
                    descripcion="Espaciado temporal irregular detectado",
                )
            )

    return ContractResult(bloqueante=False, codigo_error=None, warnings=warnings)


def _espaciado_regular(
    timestamps: list, resolucion_temporal: str | None = None
) -> bool:
    # F2.2 (Bloque F, docs/plan-etapa2-implementacion.md §7). Dos casos reales
    # distintos según de dónde vengan los timestamps:
    #
    # - CSV: parser.py::_leer_dataframe no pasa parse_dates a pd.read_csv, así
    #   que una columna de fechas llega como str crudo ("1980-01-31"). Restar
    #   dos str levanta TypeError, capturado más abajo — hoy la comparación
    #   se salta en silencio para CUALQUIER serie con fechas de texto,
    #   irregular o no, sin avisar nunca.
    # - Excel: pd.read_excel sí reconoce el tipo fecha nativo de la celda, así
    #   que la columna llega como Timestamp real. Restar dos Timestamp
    #   consecutivos de una serie MENSUAL da un Timedelta de 28, 29, 30 o 31
    #   días según el mes — nunca el mismo valor dos veces seguidas, así que
    #   `len(set(diffs)) == 1` rechaza como "irregular" una serie mensual
    #   perfectamente regular.
    #
    # Con resolucion_temporal == "mensual" se compara en granularidad de MES
    # (ordinal de período, PeriodIndex.asi8 — consecutivo por construcción),
    # no de día: dos fechas que caen en meses consecutivos dan diferencia 1,
    # sin importar si el mes tiene 28, 30 o 31 días. Para "anual" (u otros
    # casos, incluidos los timestamps año-entero que ya funcionan hoy) se
    # conserva la comparación exacta original.
    if len(timestamps) < 2:
        return True
    if resolucion_temporal == "mensual":
        try:
            ordinales = parsear_timestamps(timestamps).to_period("M").asi8
        except Exception:
            return True
        diffs = ordinales[1:] - ordinales[:-1]
        return len(set(diffs.tolist())) == 1
    try:
        diffs = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        return len(set(diffs)) == 1
    except TypeError:
        return True

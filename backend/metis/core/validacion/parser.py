import io

import pandas as pd

from metis.core.types import ParsedData


def parse_file(
    content: bytes,
    filename: str,
    columna_x: str,
    columna_y: str,
) -> ParsedData:
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(content))
    else:
        df = pd.read_csv(io.BytesIO(content))

    col_x = _resolver_columna(df, columna_x)
    col_y = _resolver_columna(df, columna_y)

    # Preservar None — validar_contrato() detecta CONTRACT_MISSING_VALUES
    serie = [float(v) if pd.notna(v) else None for v in df[col_y].tolist()]
    timestamps = (
        [v if pd.notna(v) else None for v in df[col_x].tolist()]
        if col_x is not None
        else None
    )
    resolucion_temporal = _inferir_resolucion(timestamps) if timestamps else None

    return ParsedData(
        serie=serie,
        timestamps=timestamps,
        resolucion_temporal=resolucion_temporal,
    )


def _resolver_columna(df: pd.DataFrame, columna: str) -> str | None:
    if columna in df.columns:
        return columna
    try:
        idx = int(columna)
        return df.columns[idx]
    except (ValueError, IndexError):
        return None


def _inferir_resolucion(timestamps: list) -> str | None:
    if len(timestamps) < 2:
        return None
    try:
        ts = pd.to_datetime(timestamps)
        delta = (ts[-1] - ts[0]) / (len(ts) - 1)
        if delta.days >= 300:
            return "anual"
        if delta.days >= 25:
            return "mensual"
        return None
    except Exception:
        return None

import io

import pandas as pd

from metis.core.types import ParsedData

MUESTRA_MAX = 5


def _leer_dataframe(content: bytes, filename: str) -> pd.DataFrame:
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    return pd.read_csv(io.BytesIO(content))


def leer_columnas_preview(content: bytes, filename: str) -> tuple[list[dict], int]:
    """Cabeceras + muestra de valores por columna, para POST /analysis/preview-columns
    (DECISIÓN 047). Reusa el mismo parseo pandas que parse_file() para que el
    dropdown de ConfigPage ofrezca exactamente las columnas que el pipeline
    real va a leer — nunca dos lecturas de cabeceras que puedan divergir.

    A diferencia de parse_file(), esto NO valida contrato ni corre ninguna
    prueba estadística — es una previsualización, no un análisis (plan
    pasada4 §6 D2).

    No hay una guarda explícita de "sin columnas utilizables": pandas
    levanta EmptyDataError (subclase de ValueError) antes de devolver un
    DataFrame para cualquier CSV vacío o solo-espacios — verificado, no hay
    forma de que este parseo devuelva un DataFrame con columnas=0 sin haber
    lanzado ya. El único código de error real de este camino es PARSE_ERROR
    (DECISIÓN 047, addendum).
    """
    df = _leer_dataframe(content, filename)

    columnas = []
    for indice, nombre in enumerate(df.columns):
        valores = df[nombre].head(MUESTRA_MAX).tolist()
        muestra = [str(v) for v in valores if pd.notna(v)]
        columnas.append({"nombre": str(nombre), "indice": indice, "muestra": muestra})

    return columnas, len(df)


def parse_file(
    content: bytes,
    filename: str,
    columna_x: str,
    columna_y: str,
) -> ParsedData:
    df = _leer_dataframe(content, filename)

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

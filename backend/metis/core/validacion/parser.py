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
    # F2.3 (Bloque F, docs/plan-etapa2-implementacion.md §7) — antes usaba el
    # PROMEDIO de los deltas entre timestamps consecutivos: (ts[-1]-ts[0])/(n-1).
    # Un solo hueco largo en una serie mayormente mensual (un sensor caído
    # varios meses, un año sin registro) arrastra el promedio hacia arriba y
    # puede cruzar el umbral de "anual" aunque el espaciado real y dominante
    # de la serie siga siendo mensual. La MODA de los deltas no se deja
    # arrastrar por un outlier — refleja el espaciado que la serie realmente
    # tiene la mayor parte del tiempo.
    #
    # R1.1 (docs/plan-resolucion-diaria.md) — `moda_dias == 1` es "diaria", y
    # es `== 1` a propósito, no `<= 24`:
    #   - una moda de 7 días es un registro semanal; una de 15, quincenal.
    #     Ninguno tiene regla de agregación en METIS; devolver "diaria" para
    #     ellos los haría entrar al pipeline con una noción de "año completo"
    #     que no les corresponde. Quedan en None ->
    #     CONTRACT_NO_TEMPORAL_RESOLUTION, que es honesto: METIS no sabe
    #     procesarlos.
    #   - lo sub-diario también cae en None, por un efecto de `.days`: TRUNCA.
    #     Una serie horaria da deltas de 0 días -> moda 0 -> None. Es el
    #     bloqueo correcto y deseado; va como test explícito. Si alguien
    #     reescribe la inferencia con total_seconds() tiene que preservarlo.
    if len(timestamps) < 2:
        return None
    try:
        ts = parsear_timestamps(timestamps)
        deltas_dias = (ts[1:] - ts[:-1]).days
        moda_dias = int(pd.Series(deltas_dias).mode().iloc[0])
        if moda_dias >= 300:
            return "anual"
        if moda_dias >= 25:
            return "mensual"
        if moda_dias == 1:
            return "diaria"
        return None
    except Exception:
        return None


def parsear_timestamps(timestamps: list) -> pd.DatetimeIndex:
    # Bug encontrado en verificación manual (05/08/2026): una columna de año
    # puro (ej. "anio": 1980, 1981, ...) es el caso MÁS común de este dominio
    # — series anuales de máximos hidrológicos, exactamente el formato de la
    # tesis de Facundo. pd.to_datetime() sin `format` interpreta enteros como
    # nanosegundos desde epoch, no como años: toda la serie colapsaba a
    # timestamps a nanosegundos de 1970-01-01, delta.days siempre 0, y
    # CONTRACT_NO_TEMPORAL_RESOLUTION bloqueaba el pipeline para el caso de
    # uso más común del sistema. Detectar el patrón (todos los valores son
    # años de 4 dígitos plausibles) y parsear explícitamente con format="%Y".
    valores = list(timestamps)
    if all(_es_anio_plausible(v) for v in valores):
        return pd.to_datetime([int(v) for v in valores], format="%Y")
    return pd.to_datetime(valores)


def _es_anio_plausible(valor) -> bool:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return False
    return numero == int(numero) and 1000 <= numero <= 9999

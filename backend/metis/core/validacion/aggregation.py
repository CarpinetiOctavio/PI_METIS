"""
Agregación temporal — construye la serie de máximos anuales a partir de
datos mensuales, según el mes de inicio de año configurado.

DECISIÓN 057 (Bloque F3-F4 del plan de implementación de Etapa 2): el año
hidrológico no es una constante del sistema — es un parámetro,
`mes_inicio_anio ∈ [1..12]`, con el año calendario como el caso particular
`mes_inicio_anio = 1`.

Función pura, sin conocimiento de HTTP, BD ni sesiones — misma restricción
de aislamiento que el resto de core/ (ver architecture.md).
"""

from dataclasses import dataclass, field

from metis.core.utils import es_numerico
from metis.core.validacion.parser import parsear_timestamps

# Motivos de descarte de un período — ver AgregacionResult.
MOTIVO_EXTREMO_INICIO = "extremo_inicio"
MOTIVO_EXTREMO_FIN = "extremo_fin"
MOTIVO_HUECO_INTERIOR = "hueco_interior"


@dataclass
class PeriodoDescartado:
    anio: int  # año-etiqueta del período (el año calendario en que empieza)
    motivo: str  # MOTIVO_EXTREMO_INICIO | MOTIVO_EXTREMO_FIN | MOTIVO_HUECO_INTERIOR
    meses_presentes: int
    meses_faltantes: int


@dataclass
class AgregacionResult:
    serie: list[float]  # máximos anuales, uno por período completo
    timestamps: list[int]  # año-etiqueta de cada elemento de `serie`, ascendente
    periodos_descartados: list[PeriodoDescartado] = field(default_factory=list)


def _periodo_de(anio: int, mes: int, mes_inicio: int) -> int:
    """Año-etiqueta del período al que pertenece una fecha (anio, mes).

    Un período que arranca en mes_inicio del año Y corre hasta mes_inicio-1
    de Y+1, y se etiqueta con Y (el año calendario en que empieza) — ver
    plan §7, F4 "Etiquetado del año agregado". Con mes_inicio=1 esto
    degenera exactamente en el año calendario.
    """
    return anio if mes >= mes_inicio else anio - 1


def _meses_esperados(periodo: int, mes_inicio: int) -> set[tuple[int, int]]:
    """Los 12 pares (año, mes) que forman el período año-etiqueta `periodo`."""
    meses: set[tuple[int, int]] = set()
    for i in range(12):
        mes = (mes_inicio - 1 + i) % 12 + 1
        anio = periodo if mes >= mes_inicio else periodo + 1
        meses.add((anio, mes))
    return meses


def agregar_a_maximos_anuales(
    serie: list,
    timestamps: list,
    mes_inicio: int,
) -> AgregacionResult:
    """Agrega una serie mensual a máximos anuales según `mes_inicio`.

    serie, timestamps: mismo shape que ParsedData — timestamps puede traer
    strings, años enteros o Timestamp real (Excel); se parsean acá con la
    misma parsear_timestamps() que ya usa parser.py/contract.py.

    Regla de recorte (plan §7, F4): los años parciales en los DOS extremos
    del registro se descartan, nunca se completan ni interpolan — el
    registro se recorta a años completos. Un año interior incompleto (un
    hueco en el medio del registro, no un borde) también se descarta, con
    un motivo distinto (MOTIVO_HUECO_INTERIOR) porque significa otra cosa:
    hay un agujero en el registro, no un borde natural de los datos
    disponibles.

    Un valor faltante o no numérico en un mes cuenta como si ese mes no
    estuviera presente en absoluto — rompe la completitud del período
    exactamente igual que un mes ausente del registro.

    Devuelve serie=[] si no queda ningún período completo — el pipeline lo
    trata como cualquier serie corta (CONTRACT_SERIES_TOO_SHORT si queda
    bajo el mínimo de 10).
    """
    fechas = parsear_timestamps(timestamps)

    por_periodo: dict[int, dict[tuple[int, int], float]] = {}
    for fecha, valor in zip(fechas, serie):
        if not es_numerico(valor):
            continue
        periodo = _periodo_de(fecha.year, fecha.month, mes_inicio)
        por_periodo.setdefault(periodo, {})[(fecha.year, fecha.month)] = float(valor)

    if not por_periodo:
        return AgregacionResult(serie=[], timestamps=[])

    periodo_inicio = _periodo_de(fechas[0].year, fechas[0].month, mes_inicio)
    periodo_fin = _periodo_de(fechas[-1].year, fechas[-1].month, mes_inicio)

    serie_agregada: list[float] = []
    timestamps_agregados: list[int] = []
    descartados: list[PeriodoDescartado] = []

    for periodo in range(periodo_inicio, periodo_fin + 1):
        esperados = _meses_esperados(periodo, mes_inicio)
        presentes = por_periodo.get(periodo, {})
        completo = set(presentes.keys()) == esperados

        if completo:
            serie_agregada.append(max(presentes.values()))
            timestamps_agregados.append(periodo)
            continue

        if periodo == periodo_inicio:
            motivo = MOTIVO_EXTREMO_INICIO
        elif periodo == periodo_fin:
            motivo = MOTIVO_EXTREMO_FIN
        else:
            motivo = MOTIVO_HUECO_INTERIOR

        descartados.append(
            PeriodoDescartado(
                anio=periodo,
                motivo=motivo,
                meses_presentes=len(presentes),
                meses_faltantes=12 - len(presentes),
            )
        )

    return AgregacionResult(
        serie=serie_agregada,
        timestamps=timestamps_agregados,
        periodos_descartados=descartados,
    )

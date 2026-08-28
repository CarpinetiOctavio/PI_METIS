"""
Agregación temporal — construye la serie de máximos anuales a partir de
datos mensuales o diarios, según el mes de inicio de año configurado.

DECISIÓN 057 (Bloque F3-F4 del plan de implementación de Etapa 2): el año
hidrológico no es una constante del sistema — es un parámetro,
`mes_inicio_anio ∈ [1..12]`, con el año calendario como el caso particular
`mes_inicio_anio = 1`.

docs/plan-resolucion-diaria.md (R2) — generalización a resolución diaria.
`agregar_a_maximos_anuales()` gana dos parámetros con default que reproduce
exactamente el comportamiento mensual ya auditado:
  - `resolucion`: "mensual" | "diaria" — decide la granularidad de la
    unidad de completitud (12 meses vs. 365/366 días).
  - `cobertura_minima_interior`: fracción de unidades presentes que hace
    aceptable el máximo de un año INTERIOR. Los años de los extremos
    siempre exigen 100 % (regla asimétrica, R2.3 — DECISIÓN 057 descarta
    los extremos parciales por el sesgo a la baja, y en un extremo la
    parcialidad es la regla). Valor provisorio 1.0 (estricto) mientras
    R0.1 espera respuesta de Facundo — con 1.0 esto es equivalente a la
    igualdad de conjuntos del código mensual original.

Función pura, sin conocimiento de HTTP, BD ni sesiones — misma restricción
de aislamiento que el resto de core/ (ver architecture.md).
"""

from dataclasses import dataclass, field

import pandas as pd

from metis.core.utils import es_numerico
from metis.core.validacion.parser import parsear_timestamps

# Motivos de descarte de un período — ver AgregacionResult.
MOTIVO_EXTREMO_INICIO = "extremo_inicio"
MOTIVO_EXTREMO_FIN = "extremo_fin"
MOTIVO_HUECO_INTERIOR = "hueco_interior"

# Cobertura mínima de unidades para aceptar el máximo de un año interior,
# por resolución de entrada (R0.1 / R3.1). Provisorio en 1.0 (estricto) —
# el parámetro está cableado y probado para aceptar valores menores, pero
# relajarlo necesita evidencia de registros reales de Facundo (ver el plan
# §R0.1). Los años de los EXTREMOS ignoran esto: siempre exigen 100 %.
COBERTURA_MINIMA_INTERIOR: dict[str, float] = {
    "mensual": 1.0,
    "diaria": 1.0,
}


@dataclass
class PeriodoDescartado:
    anio: int  # año-etiqueta del período (el año calendario en que empieza)
    motivo: str  # MOTIVO_EXTREMO_INICIO | MOTIVO_EXTREMO_FIN | MOTIVO_HUECO_INTERIOR
    unidades_presentes: int  # meses o días con dato numérico
    unidades_faltantes: int  # unidades_esperadas - unidades_presentes
    unidades_esperadas: int  # 12 (mensual) o 365/366 (diaria)


@dataclass
class PeriodoAceptadoConHueco:
    """Año INTERIOR aceptado con cobertura < 100 % (posible solo con
    `cobertura_minima_interior < 1.0`, R2.3). Su máximo entra a la serie,
    pero está sesgado a la baja — el warning de agregación tiene que
    exponerlo (CONTRACT_INCOMPLETE_YEARS_ACCEPTED), no puede quedar
    invisible. Con el valor provisorio 1.0 esta lista siempre está vacía.
    """

    anio: int
    unidades_presentes: int
    unidades_faltantes: int
    unidades_esperadas: int


@dataclass
class AgregacionResult:
    serie: list[float]  # máximos anuales, uno por período completo
    timestamps: list[int]  # año-etiqueta de cada elemento de `serie`, ascendente
    periodos_descartados: list[PeriodoDescartado] = field(default_factory=list)
    periodos_incompletos_aceptados: list[PeriodoAceptadoConHueco] = field(
        default_factory=list
    )


def _periodo_de(anio: int, mes: int, mes_inicio: int) -> int:
    """Año-etiqueta del período al que pertenece una fecha (anio, mes).

    Un período que arranca en mes_inicio del año Y corre hasta mes_inicio-1
    de Y+1, y se etiqueta con Y (el año calendario en que empieza) — ver
    plan §7, F4 "Etiquetado del año agregado". Con mes_inicio=1 esto
    degenera exactamente en el año calendario.

    Depende solo de año y mes: una fecha diaria cae en el mismo período que
    su mes. Es la razón de fondo por la que la generalización a diaria es
    barata — `mes_inicio_anio` sigue operando en granularidad de mes sin
    importar la resolución del dato.
    """
    return anio if mes >= mes_inicio else anio - 1


def _esperados(periodo: int, mes_inicio: int, resolucion: str) -> set[tuple]:
    """Las unidades (meses o días) que forman el período año-etiqueta.

    - "mensual": los 12 pares (año, mes).
    - "diaria": las claves (año, mes, día) de todos los días entre el
      primer día del período y el último. Los bisiestos salen gratis —
      pd.date_range los resuelve. Ojo con mes_inicio ≠ 1: el febrero del
      período es el del año SIGUIENTE al año-etiqueta (el período que
      arranca en marzo de 2015 termina en febrero de 2016 y espera 366
      días); date_range lo resuelve solo.
    """
    if resolucion == "diaria":
        inicio = pd.Timestamp(year=periodo, month=mes_inicio, day=1)
        fin = inicio + pd.DateOffset(years=1) - pd.Timedelta(days=1)
        dias = pd.date_range(inicio, fin, freq="D")
        return {(d.year, d.month, d.day) for d in dias}

    meses: set[tuple[int, int]] = set()
    for i in range(12):
        mes = (mes_inicio - 1 + i) % 12 + 1
        anio = periodo if mes >= mes_inicio else periodo + 1
        meses.add((anio, mes))
    return meses


def _clave_unidad(fecha, resolucion: str) -> tuple:
    """Clave de agrupación de una fecha dentro de su período.

    CRÍTICO para diaria: con la clave en granularidad de mes, el diccionario
    de `agregar_a_maximos_anuales()` se quedaría con el ÚLTIMO día de cada
    mes y descartaría el resto en silencio (asigna, no maximiza) — un
    máximo anual plausible pero incorrecto. La clave TIENE que incluir el
    día cuando `resolucion == "diaria"`.
    """
    if resolucion == "diaria":
        return (fecha.year, fecha.month, fecha.day)
    return (fecha.year, fecha.month)


def agregar_a_maximos_anuales(
    serie: list,
    timestamps: list,
    mes_inicio: int,
    resolucion: str = "mensual",
    cobertura_minima_interior: float = 1.0,
) -> AgregacionResult:
    """Agrega una serie mensual o diaria a máximos anuales según `mes_inicio`.

    serie, timestamps: mismo shape que ParsedData — timestamps puede traer
    strings, años enteros o Timestamp real (Excel); se parsean acá con la
    misma parsear_timestamps() que ya usa parser.py/contract.py.

    `resolucion` ("mensual" | "diaria") decide la granularidad de la unidad
    de completitud. `cobertura_minima_interior` es la fracción de unidades
    presentes que hace aceptable el máximo de un año INTERIOR — los años de
    los EXTREMOS siempre exigen 100 % (regla asimétrica, R2.3). Con
    `cobertura_minima_interior = 1.0` esto es equivalente a la igualdad de
    conjuntos del código mensual original (`presentes ⊆ esperados` siempre,
    por construcción de la clave), así que no cambia la semántica para
    mensual — la contiene como caso particular. Mismo tipo de verificación
    de consistencia que DECISIÓN 057 con `mes_inicio = 1`.

    Regla de recorte (plan §7, F4): los años parciales en los DOS extremos
    del registro se descartan, nunca se completan ni interpolan. Un año
    interior incompleto se descarta con un motivo distinto
    (MOTIVO_HUECO_INTERIOR) si su cobertura no alcanza el umbral interior;
    si lo alcanza pero está por debajo de 100 %, se acepta y se registra en
    `periodos_incompletos_aceptados` para que el warning lo exponga.

    Un valor faltante o no numérico en una unidad cuenta como si esa unidad
    no estuviera presente — rompe la completitud del período exactamente
    igual que una unidad ausente del registro.

    Devuelve serie=[] si no queda ningún período completo — el pipeline lo
    trata como cualquier serie corta (CONTRACT_SERIES_TOO_SHORT si queda
    bajo el mínimo de 10).
    """
    fechas = parsear_timestamps(timestamps)

    por_periodo: dict[int, dict[tuple, float]] = {}
    for fecha, valor in zip(fechas, serie):
        if not es_numerico(valor):
            continue
        periodo = _periodo_de(fecha.year, fecha.month, mes_inicio)
        clave = _clave_unidad(fecha, resolucion)
        por_periodo.setdefault(periodo, {})[clave] = float(valor)

    if not por_periodo:
        return AgregacionResult(serie=[], timestamps=[])

    periodo_inicio = _periodo_de(fechas[0].year, fechas[0].month, mes_inicio)
    periodo_fin = _periodo_de(fechas[-1].year, fechas[-1].month, mes_inicio)

    serie_agregada: list[float] = []
    timestamps_agregados: list[int] = []
    descartados: list[PeriodoDescartado] = []
    aceptados_con_hueco: list[PeriodoAceptadoConHueco] = []

    for periodo in range(periodo_inicio, periodo_fin + 1):
        esperados = _esperados(periodo, mes_inicio, resolucion)
        presentes = por_periodo.get(periodo, {})
        n_esperadas = len(esperados)
        n_presentes = len(presentes)
        cobertura = n_presentes / n_esperadas
        es_extremo = periodo in (periodo_inicio, periodo_fin)
        umbral = 1.0 if es_extremo else cobertura_minima_interior

        if cobertura >= umbral:
            serie_agregada.append(max(presentes.values()))
            timestamps_agregados.append(periodo)
            if cobertura < 1.0:
                # año interior aceptado con hueco (solo posible con
                # cobertura_minima_interior < 1.0) — sesgo a la baja, el
                # warning lo tiene que exponer.
                aceptados_con_hueco.append(
                    PeriodoAceptadoConHueco(
                        anio=periodo,
                        unidades_presentes=n_presentes,
                        unidades_faltantes=n_esperadas - n_presentes,
                        unidades_esperadas=n_esperadas,
                    )
                )
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
                unidades_presentes=n_presentes,
                unidades_faltantes=n_esperadas - n_presentes,
                unidades_esperadas=n_esperadas,
            )
        )

    return AgregacionResult(
        serie=serie_agregada,
        timestamps=timestamps_agregados,
        periodos_descartados=descartados,
        periodos_incompletos_aceptados=aceptados_con_hueco,
    )


def agregar_a_maximos_mensuales(
    serie: list, timestamps: list
) -> tuple[list[float], list[str]]:
    """Diaria → máximos MENSUALES. Solo para la vista descriptiva del
    payload (R3.3 opción 2, docs/plan-resolucion-diaria.md): con carga
    diaria el bloque `datos` de result_etapa1 no lleva la serie diaria
    cruda (~14.600 ítems, ~637 KB — contradice el dimensionamiento de
    DECISIÓN 058), lleva esta agregación (~480 ítems para 40 años).

    NO alimenta la serie anual — esa se construye por el camino directo
    diaria → anual en `agregar_a_maximos_anuales()`. La transformación
    ocurre únicamente en la serialización
    (services/analysis_service.py::_serializar_etapa1); dos series
    comparadas en el mismo gráfico calculadas con métodos distintos es
    exactamente lo que R0.3 resolvió no hacer, así que
    Etapa1Result.serie_original sigue siendo la serie diaria cruda.

    Devuelve (serie_mensual, timestamps_iso) — un valor por mes presente,
    timestamp "YYYY-MM-01", en orden cronológico.
    """
    fechas = parsear_timestamps(timestamps)
    por_mes: dict[tuple[int, int], float] = {}
    for fecha, valor in zip(fechas, serie):
        if not es_numerico(valor):
            continue
        clave = (fecha.year, fecha.month)
        v = float(valor)
        if clave not in por_mes or v > por_mes[clave]:
            por_mes[clave] = v
    claves = sorted(por_mes)
    return (
        [por_mes[k] for k in claves],
        [f"{anio:04d}-{mes:02d}-01" for (anio, mes) in claves],
    )

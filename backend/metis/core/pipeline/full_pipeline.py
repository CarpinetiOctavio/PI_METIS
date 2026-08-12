"""
Pipeline completo — encadena Etapa 1 y Etapa 2, código puro sin
conocimiento de HTTP, BD ni sesiones (misma restricción que el resto de core/).

Etapa 2 corre siempre que Etapa 1 no haya sido rechazada, sin importar si
los warnings producidos son normales o críticos — RF-GEN-P-03: el pipeline
corre completo sin importar el nivel de warning. El único estado que
bloquea es nivel_confianza == "rechazado" (< 10 datos o serie vacía),
ya resuelto dentro del propio contrato de Etapa 1 antes de llegar acá.
Consistente con el comportamiento de referencia de la tesis (estación
Alpa Corral: rechazo unánime de Etapa 1, Etapa 2 se corrió igual con
advertencia).

La elección de alcance del usuario (solo Etapa 1 vs. pipeline completo,
RF-CU01-04) no se resuelve acá — es una decisión de orquestación previa
a la ejecución que vive en services/, no una condición del propio motor
estadístico.

services/analysis_service.py NO llama a ejecutar_pipeline_completo() —
es deliberado, no un descuido (ver docs/decisiones/decision055.md,
DECISIÓN 055). Esta función corre las dos etapas de un tirón, sin ningún
punto donde el llamador pueda observar progreso ni pausar; el stream SSE
necesita emitir Etapa 1 prueba por prueba, pausar en Chow, y solo después
pausar de nuevo en la selección de distribución de Etapa 2 — ningún punto
de acá ofrece esa granularidad. analysis_service llama ejecutar_etapa1()
y ejecutar_etapa2() por separado, con su propia orquestación. Esta función
sigue viva porque es exactamente lo que necesitan los tests de regresión
matemática (tests/regression/, Bloque D del plan de Etapa 2): comparar
contra las 9 estaciones de la tesis no requiere streaming, requiere las
dos etapas encadenadas de punta a punta sobre una serie de fixture — que
es lo que esta función ya hace. Si estás por cablear services/ a esta
función porque "hace exactamente lo que el stream necesita", no lo hagas
sin releer DECISIÓN 055 primero.
"""

import numpy as np

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1
from metis.core.pipeline.pipeline_etapa2 import ejecutar_etapa2
from metis.core.pipeline.types import FullPipelineResult


def ejecutar_pipeline_completo(
    serie: list,
    tipo_variable: str,
    resolucion_temporal: str | None = None,
    timestamps: list | None = None,
    cramer_particion: dict | str = "default",
    mes_inicio_anio: int = 7,
) -> FullPipelineResult:
    etapa1 = ejecutar_etapa1(
        serie=serie,
        tipo_variable=tipo_variable,
        resolucion_temporal=resolucion_temporal,
        timestamps=timestamps,
        cramer_particion=cramer_particion,
        mes_inicio_anio=mes_inicio_anio,
    )

    if etapa1.nivel_confianza == "rechazado":
        return FullPipelineResult(etapa1=etapa1, etapa2=None)

    # Bloque F4 — serie_efectiva, no filtrar_numericos(serie): si
    # resolucion_temporal era "mensual", serie es la serie mensual cruda,
    # y Etapa 2 tiene que ajustar sobre los máximos anuales agregados
    # (etapa1.serie_efectiva), no sobre los valores mensuales sin agregar.
    serie_np = np.asarray(etapa1.serie_efectiva, dtype=float)
    tiene_ceros = bool(np.any(serie_np == 0))

    etapa2 = ejecutar_etapa2(serie_np, tiene_ceros=tiene_ceros)

    return FullPipelineResult(etapa1=etapa1, etapa2=etapa2)

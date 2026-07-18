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
"""

import numpy as np

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1
from metis.core.pipeline.pipeline_etapa2 import ejecutar_etapa2
from metis.core.pipeline.types import FullPipelineResult
from metis.core.utils import filtrar_numericos


def ejecutar_pipeline_completo(
    serie: list,
    tipo_variable: str,
    resolucion_temporal: str | None = None,
    timestamps: list | None = None,
    cramer_particion: dict | str = "default",
) -> FullPipelineResult:
    etapa1 = ejecutar_etapa1(
        serie=serie,
        tipo_variable=tipo_variable,
        resolucion_temporal=resolucion_temporal,
        timestamps=timestamps,
        cramer_particion=cramer_particion,
    )

    if etapa1.nivel_confianza == "rechazado":
        return FullPipelineResult(etapa1=etapa1, etapa2=None)

    valores_numericos = filtrar_numericos(serie)
    serie_np = np.asarray(valores_numericos, dtype=float)
    tiene_ceros = bool(np.any(serie_np == 0))

    etapa2 = ejecutar_etapa2(serie_np, tiene_ceros=tiene_ceros)

    return FullPipelineResult(etapa1=etapa1, etapa2=etapa2)

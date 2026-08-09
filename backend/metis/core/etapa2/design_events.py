"""
Eventos de diseño — cuantil de la distribución ajustada para cada período
de retorno pedido por el usuario.

Función pura, sin conocimiento de HTTP, BD ni sesiones (misma restricción
de aislamiento que el resto de core/ — ver architecture.md).

F = 1 - 1/T   (Weibull, misma fórmula que empirical.py::probabilidades_weibull,
               acá aplicada al T que el usuario pide, no al de la muestra)
xT = modulo.cuantil(F, parametros)

Bloque A4 del plan de implementación de Etapa 2.
"""

from metis.core.etapa2.types import EventoDiseno


def calcular_eventos_diseno(
    modulo,
    parametros: dict,
    periodos_retorno: list[float],
) -> list[EventoDiseno]:
    """
    modulo:          módulo de la distribución elegida (ej. metis.core.etapa2.distributions.gumbel)
    parametros:       dict de parámetros ya ajustados de esa distribución+método
    periodos_retorno: lista de T pedidos por el usuario (todos > 1, validado en el borde)

    Un T que haga fallar cuantil() para esta distribución puntual no tumba
    el cálculo completo — ese evento se registra con valor=None y se sigue
    con el resto. Es el mismo principio que rige todo Etapa 2: ningún caso
    especial detiene el pipeline.
    """
    eventos: list[EventoDiseno] = []
    for periodo_retorno in periodos_retorno:
        f = 1.0 - 1.0 / periodo_retorno
        try:
            valor = modulo.cuantil(f, parametros)
        except Exception:
            valor = None
        eventos.append(EventoDiseno(periodo_retorno=periodo_retorno, valor=valor))
    return eventos

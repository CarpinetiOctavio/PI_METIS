# Distribuciones confirmadas como No Aplicables si algún xi = 0 o xi < 0.
# Fuente: Tesis Facundo + confirmación de Octavio.
DISABLED_WITH_ZEROS: frozenset[str] = frozenset(
    {
        "lognormal2p",
        "logpearson3",
        "gamma2p",
        "exponencial_beta",
    }
)

# Distribuciones cuyo comportamiento ante ceros está pendiente de confirmación
# con Facundo — pregunta de DOMINIO (¿tiene sentido físico un cero para esta
# variable?), no de mecánica de cálculo. Ver core-etapa2-implementation.md —
# pendientes ítem 2 y 3, y pendientes-facundo.md, sección "Etapa 2 —
# comportamiento ante ceros de 5 distribuciones".
#
# NO implica que estén bloqueadas. DECISIÓN 060 (docs/decisiones/decision060.md)
# estableció que, mientras se espera esa confirmación, el default de
# implementación de METIS es calcular igual donde la fórmula lo permite
# (con advertencia DIST_ZEROS_TOLERATED, ver TOLERA_CEROS_CON_ADVERTENCIA más
# abajo) — no bloquear por las dudas. Esto resuelve únicamente el default
# mientras se espera, no la pregunta de dominio en sí, que sigue abierta.
PENDING_ZEROS_CONFIRMATION: frozenset[str] = frozenset(
    {
        "gamma3p",
        "exponencial_x0_beta",
        "gen_pareto",
        "lognormal3p",
        "gen_exponencial",
    }
)

# Subconjunto de PENDING_ZEROS_CONFIRMATION cuyo módulo emite DIST_ZEROS_TOLERATED
# cuando calcula con un cero presente en la serie (pipeline_etapa2.py es quien
# efectivamente dispara la advertencia — este set solo indica a qué distribuciones
# aplica). gamma3p y lognormal3p quedan fuera aunque también toleran cero desde
# antes de DECISIÓN 060 — no emitían advertencia previamente y esa laguna no se
# cierra acá, queda señalada en decision060.md para decidir aparte.
#
# gen_exponencial entra pese a que su método MV sigue bloqueando (log(1-e^-λx)
# indefinido en x=0, necesidad matemática real, no pendiente de dominio) — el
# warning solo se dispara cuando el método efectivamente calcula (status=ok),
# nunca para MV con cero presente (ese caso sigue devolviendo disabled_zeros).
TOLERA_CEROS_CON_ADVERTENCIA: frozenset[str] = frozenset(
    {
        "exponencial_x0_beta",
        "gen_pareto",
        "gen_exponencial",
    }
)

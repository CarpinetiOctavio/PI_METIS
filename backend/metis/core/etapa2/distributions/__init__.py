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
# con Facundo. Se tratan como disabled_zeros hasta recibir confirmación.
# Ver core-etapa2-implementation.md — pendientes ítem 2 y 3.
PENDING_ZEROS_CONFIRMATION: frozenset[str] = frozenset(
    {
        "gamma3p",
        "exponencial_x0_beta",
        "gen_pareto",
        "lognormal3p",
        "gen_exponencial",
    }
)

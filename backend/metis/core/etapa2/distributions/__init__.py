# Distribuciones confirmadas como No Aplicables si algún xi = 0 o xi < 0.
# Fuente: Tesis Facundo + confirmación de Octavio.
DISABLED_WITH_ZEROS: frozenset[str] = frozenset(
    {
        "log_normal_2p",
        "log_pearson_3",
        "gamma_2p",
        "exponencial_beta",
    }
)

# Distribuciones cuyo comportamiento ante ceros está pendiente de confirmación
# con Facundo. Se tratan como disabled_zeros hasta recibir confirmación.
# Ver core-etapa2-implementation.md — pendientes ítem 2 y 3.
PENDING_ZEROS_CONFIRMATION: frozenset[str] = frozenset(
    {
        "gamma_3p",
        "exponencial_x0_beta",
        "gen_pareto",
        "log_normal_3p",
        "gen_exponencial",
    }
)

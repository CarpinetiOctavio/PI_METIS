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

# Distribuciones no definidas para valores negativos (DECISIÓN 073). Las cuatro
# primeras ya devolvían no_aplicable con serie <= 0 y gen_exponencial con
# serie < 0; ahora el pipeline marca el motivo con disabled_negatives. Las de 3
# parámetros (lognormal3p, gamma3p, exponencial_x0_beta, gen_pareto) NO entran:
# estiman un parámetro de posición y deciden por su cuenta con su chequeo
# x0 >= min(serie). Depende de los datos, no de tipo_variable.
DISABLED_WITH_NEGATIVES: frozenset[str] = frozenset(
    {
        "lognormal2p",
        "logpearson3",
        "gamma2p",
        "exponencial_beta",
        "gen_exponencial",
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

# Distribuciones que se calculan y se muestran, pero que NO se pueden elegir,
# nunca llevan "menor EEA" y van al final del ranking (DECISIÓN 074,
# docs/decisiones/decision074.md). Sus fórmulas de referencia tienen una
# inconsistencia conocida en la fuente que todavía no se corrigió.
#
# gen_pareto: la sección IV.3.10 de la tesis mezcla dos convenciones de signo
# del parámetro de forma (los estimadores en la de Hosking, la función de
# distribución IV-146 y el cuantil IV-174 en la de Coles), IV-167 tiene el signo
# del numerador cambiado, y Mínimos Cuadrados (IV-153/IV-155) no recupera el
# parámetro. El código reproduce la tesis fielmente; la corrección queda para la
# V2. Diagnóstico completo:
# docs/auditoria/hallazgos/hallazgo-gen-pareto-convenciones.md.
#
# Cuando una distribución se corrige, sale de acá; el mecanismo queda para
# futuros casos. CU-03 (selección automática por menor EEA) tiene que saltear
# las que estén en este conjunto.
PENDIENTES_VALIDACION: frozenset[str] = frozenset({"gen_pareto"})

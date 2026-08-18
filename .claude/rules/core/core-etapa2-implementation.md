# Implementación del Core — Etapa 2

## Librerías permitidas
- numpy — operaciones vectoriales, logaritmos, ordenamiento
- scipy.stats — distribuciones de probabilidad (pdf, cdf, ppf)
- scipy.optimize — métodos iterativos (MV de Log-Pearson III, GVE)
- scipy.special — función gamma y derivadas (Pearson III, Gamma)
- math, statistics — solo para casos donde numpy no aplica

## Restricción absoluta
Ver architecture.md — "core/ completamente aislado" para la restricción de imports.

## Criterio de convergencia
1×10⁻⁷ — fijo, no configurable. Aplica a todos los métodos iterativos.

## Fórmula de probabilidades empíricas
Weibull: T = (n+1)/m, P = 1 - 1/T
Fuente: tesis Facundo.

## Criterio de ranking
EEA (Error Estándar de Ajuste) — menor es mejor.
Criterio de desempate: menor número de parámetros.
Fuente: tesis Facundo.

## Distribuciones prioritarias (confirmar con Facundo primero)
Gumbel, GVE, Log-Pearson III, Normal, Log-Normal 2p.

## Distribuciones deshabilitadas ante ceros — confirmadas
- Log-Normal 2p
- Log-Pearson III  
- Gamma 2p
- Exponencial (β)

## Distribuciones con comportamiento ante ceros — PENDIENTE Facundo
- Gamma 3p
- Exponencial (x₀, β)
- Generalizada de Pareto
- Log-Normal 3p
- Generalizada Exponencial

Implementar con PENDING_ZEROS_CONFIRMATION = True visible en el código.
No asumir comportamiento — esperar confirmación de Facundo. Esto sigue
sin cambios: la pregunta de dominio (¿tiene sentido físico un cero para
estas variables?) no está resuelta.

**DECISIÓN 061 (17/08/2026, `docs/decisiones/decision061.md`) fijó el
default de implementación mientras se espera esa confirmación — no
confundir con haberla resuelto.** Verificado método por método que de
las 5 distribuciones de arriba, solo Generalizada Exponencial/MV tiene
una necesidad matemática real de bloquear (`log(1-e^-λx)` indefinido en
x=0). Las otras 8 combinaciones distribución/método (Gamma 3p y
Log-Normal 3p completas; Exponencial x0-β completa; Generalizada de
Pareto completa; Gen. Exponencial/Momentos y /ML) no tienen ninguna
operación que un cero rompa, así que calculan igual y emiten
`DIST_ZEROS_TOLERATED` en vez de `STATUS_DISABLED_ZEROS`. Ver
`TOLERA_CEROS_CON_ADVERTENCIA` en
`metis/core/etapa2/distributions/__init__.py` para el detalle exacto de
qué combinación cae en qué categoría.

## Métodos de estimación — estado
Confirmados: Momentos, MV, ML (Momentos-L Hosking 1990), MPP
Pendientes de confirmación con Facundo: ME, MC
GVE + ML: usar aproximación de Hosking (1985) para estimar κ.

## Casos especiales — nunca detienen el pipeline
- no_converge: método iterativo sin solución estable
- no_aplicable: combinación sin sentido matemático para esos datos
- disabled_zeros: distribución deshabilitada por ceros
- high_eea: EEA > 5% de la media → warning DIST_HIGH_EEA

## Preguntas pendientes con Facundo
Ver `docs/auditoria/pendientes/pendientes-facundo.md`:
- ME/MC — sección "Etapa 2 — ¿ME y MC = Mínimos Cuadrados Estándar y Corregidos?".
- Comportamiento ante ceros de las 5 distribuciones (listadas arriba) —
  sección "Etapa 2 — comportamiento ante ceros de 5 distribuciones".
- Fórmula de EEA — ya verificada y superada, sección "Discrepancias en
  EEA sin explicación (Causa C)" (líneas 194-249) y Causa D (línea 442).
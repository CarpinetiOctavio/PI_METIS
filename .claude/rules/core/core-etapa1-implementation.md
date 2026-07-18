# Implementación del Core Estadístico

## Librerías permitidas
- numpy — operaciones vectoriales, logaritmos, media, desvío
- scipy.stats.t — valor crítico t de Student (Helmert, Cramer, t-Student)
- scipy.stats.norm — valor crítico normal estándar (Wald-Wolfowitz n > 40)
- pymannkendall — Mann-Kendall n > 10 (fórmula A.55)
- math, statistics — solo para casos donde numpy no aplica

## Restricción absoluta
Ver architecture.md — "core/ completamente aislado" para la restricción de imports.

## Fuentes por prueba
- Anderson: fórmula analítica tesis Facundo Cap. III
- Wald-Wolfowitz: normal estándar n > 40, tabla hardcodeada n ≤ 40
- Helmert: fórmula directa
- t de Student: scipy.stats.t con ν = n1 + n2 - 2
- Cramer: scipy.stats.t, partición 60%/30% default, siempre incluir n1 y n2
- Mann-Kendall: pymannkendall n > 10, Tabla A.4 hardcodeada n ≤ 10
- KS tendencia: Z_crit = 1.358 hardcodeado (Tabla A.5)
- Chow: sobre logaritmos, fuente Escalante Sandoval & Reyes Chávez 2005

## Criterio de convergencia
1×10⁻⁷ — aplica a métodos iterativos de Etapa 2

## α fijo
0.05 — no es parámetro configurable en V1.0

## Separación de responsabilidades — flujo de datos
Ver architecture.md — "Separación de responsabilidades — flujo de datos".

## Decisiones de implementación tomadas

### Helmert — valor crítico
Usa normal estándar (1.96) en lugar de t de Student,
consistente con la tesis de Facundo. Para series cortas
puede haber diferencia marginal — decisión documentada
y aceptada. No cambiar sin consultar a Facundo.

### Chow — K_N vía Grubbs-Beck (Bulletin 17B) — DECISIÓN 018, PROVISORIO
El valor crítico es K_N (transformación geométrica de Grubbs-Beck sobre
un cuantil t con corrección de Bonferroni, ν=n-2, α=0.10), no el cuantil
t crudo. La nota anterior de este archivo afirmaba que el cuantil t
crudo (ν=n-1, α=0.05) era "la implementación correcta según Escalante
Sandoval & Reyes Chávez (2005)" — esa afirmación nunca fue verificada
contra el paper de Escalante, y la fórmula de Escalante es distinta de
Grubbs-Beck (confirmado por Octavio). Ante la imposibilidad de verificar
Escalante a tiempo, se optó por Grubbs-Beck/Bulletin 17B — fuente pública
y más rigurosa — como decisión explícitamente provisoria. Revisar si
Facundo/Carlos confirman Escalante u otra fuente. Ver DECISIÓN 018,
docs/decisiones/decision018.md, y formulas-etapa1.md Sección 9.

### Mann-Kendall Tabla A.4 — n=7 pendiente
Ver `docs/auditoria/pendientes/pendientes-facundo.md` — sección
"Mann-Kendall — Tabla A.4, valor crítico de S para n=7".

### pipeline.py — filtrado de serie
Las pruebas estadísticas reciben solo los valores numéricos
filtrados — no la serie original. contract.py filtra los no
numéricos antes de contar. pipeline.py debe pasar
valores_numericos a todas las pruebas, nunca serie cruda.


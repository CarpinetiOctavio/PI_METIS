# Implementación del Core Estadístico

## Librerías permitidas
- numpy — operaciones vectoriales, logaritmos, media, desvío
- scipy.stats.t — valor crítico t de Student (Helmert, Cramer, t-Student)
- scipy.stats.norm — valor crítico normal estándar (Wald-Wolfowitz n > 40)
- pymannkendall — Mann-Kendall n > 10 (fórmula A.55)
- math, statistics — solo para casos donde numpy no aplica

## Restricción absoluta
core/ no importa nada de api/, services/, db/ ni auth/.
Verificar antes de cada commit con:
grep -r "from metis.api\|from metis.services\|from metis.db\|from metis.auth" metis/core/

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

El flujo de datos desde el request hasta el core sigue
este orden estricto. Cada capa tiene una única responsabilidad:

api/        → recibe el request HTTP, valida con Pydantic,
              genera session_id, delega a services/
              NO parsea archivos, NO ejecuta lógica de negocio

core/parser.py → extrae serie, timestamps y resolucion_temporal
                 del UploadFile. Devuelve tipos Python puros.
                 NO sabe que existe HTTP ni BD

services/   → orquesta el pipeline: llama a core/parser.py,
              llama a core/pipeline.py, emite eventos SSE,
              persiste en BD si hay user_id
              NO recibe UploadFile, NO define endpoints

core/       → ejecuta pruebas estadísticas sobre tipos Python puros
              NO sabe que existe HTTP, BD, archivos ni sesiones

Cualquier lógica que no encaje claramente en una de estas
capas es señal de que falta un módulo nuevo.

## Decisiones de implementación tomadas

### Helmert — valor crítico
Usa normal estándar (1.96) en lugar de t de Student,
consistente con la tesis de Facundo. Para series cortas
puede haber diferencia marginal — decisión documentada
y aceptada. No cambiar sin consultar a Facundo.

### Chow — corrección de Bonferroni
El valor crítico usa t_dist.ppf(1 - α/(2*n)) — corrección
de Bonferroni para evaluar n observaciones simultáneamente.
Es la implementación correcta según Escalante Sandoval &
Reyes Chávez (2005). No cambiar.

### Mann-Kendall Tabla A.4 — n=7 pendiente
El valor crítico de S para n=7 no está confirmado por Facundo.
La prueba retorna no_ejecutada con TEST_NOT_EXECUTED_CONDITION
para n=7 hasta que se confirme. Consultar a Facundo con la
pregunta: "¿Cuál es el valor crítico de S para n=7 en la
Tabla A.4 de Mann-Kendall a α=5%?"

### pipeline.py — filtrado de serie
Las pruebas estadísticas reciben solo los valores numéricos
filtrados — no la serie original. contract.py filtra los no
numéricos antes de contar. pipeline.py debe pasar
valores_numericos a todas las pruebas, nunca serie cruda.

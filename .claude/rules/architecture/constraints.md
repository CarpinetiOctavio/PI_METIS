# Restricciones y Comportamientos No Negociables

## Lo que NUNCA se cambia sin consultar a Octavio

### Stack
- Python en backend — no agregar otros lenguajes de backend
- PostgreSQL — no reemplazar por SQLite ni ninguna otra BD
- React + TypeScript — no JavaScript puro ni otro framework

### Seguridad
- JWT en HttpOnly Cookie — nunca en localStorage ni sessionStorage
- API Keys almacenadas como hash bcrypt — nunca texto plano en BD
- Variables de entorno en .env — nunca credenciales en código
- .env nunca se commitea — está en .gitignore desde el inicio
- auth/ implementado: usuario/contraseña + bcrypt + JWT HttpOnly Cookie con verificación @ucc.edu.ar (DECISIÓN 001). Parte 2 (envío real de mail con `aiosmtplib`): credenciales de IT recibidas 10/06, implementación pendiente de iniciar (DECISIÓN 004).

### Lógica de negocio
- α = 5% fijo — no es configurable por el usuario en V1.0
- El pipeline siempre arranca por Etapa 1 — nunca se puede ejecutar Etapa 2 directamente
- METIS no sugiere distribución ganadora — presenta el ranking, el usuario decide
- METIS no corrige datos — detecta, advierte, y continúa (excepto CU-03 con auto_clean=true)
- Chow aplica sobre logaritmos — si hay ceros en caudal_precipitacion, marcar como no_ejecutada

### CU-03
- CU-03 expone solo Etapa 1 — nunca Etapa 2
- CU-03 es completamente stateless — ningún estado entre llamadas
- CU-03 no tiene endpoint outlier-decision ni design-events

---

## Comportamientos específicos que se implementan tal como están

### Wald-Wolfowitz con n ≤ 40
NO omitir. NO bloquear. Ejecutar CON advertencia explícita `TEST_WARNING_SMALL_SAMPLE`.
Fuente: Facundo — reunión 14/04.

### Anderson acepta, Wald-Wolfowitz rechaza
Resultado final = INDEPENDIENTE. Incluir nota del resultado de Wald en el output.
Anderson manda en independencia.

### Cramer rechaza homogeneidad
→ nivel = `homogeneidad_critica` → warning CRÍTICO.
No importa si Helmert o t de Student aprobaron.

### Chow detecta atípico — CU-01/CU-02
Stream pausa. Se emite evento `outlier_detected`. El pipeline NO continúa hasta recibir
decisión del usuario via POST /analysis/outlier-decision.

### Año hidrológico — configurable, no una constante (DECISIÓN 057)
**Corrección 12/08/2026:** esta sección decía "calendario (ene-dic) e
hidrológico (jul-jun)" como si fueran las dos únicas opciones del sistema.
Julio-junio es el año hidrológico de la región centro de Argentina (donde
están las 9 estaciones de la tesis de Facundo) — un valor por defecto
razonable, no una regla universal. Un registro del NOA, de la cuenca del
Plata o de la Patagonia arranca la temporada húmeda en otro mes.

El mes de inicio del año se configura antes de correr el análisis:
`mes_inicio_anio ∈ [1..12]` (`POST /analysis/stream`, default `7`). El año
calendario es simplemente el caso `mes_inicio_anio = 1`, no un modo aparte
con un toggle — ver `core/validacion/aggregation.py::agregar_a_maximos_anuales()`
y `docs/decisiones/decision057.md`.

**Aplica a resolución mensual y diaria.** Desde `docs/decisiones/decision065.md`
(28/08/2026) `agregar_a_maximos_anuales()` acepta `resolucion="diaria"`
además de `"mensual"`, por el mismo camino A y directo diaria→anual (no
encadenado). La unidad de completitud de un año pasa de 12 meses a 365/366
días (bisiestos incluidos, también el febrero del año siguiente cuando
`mes_inicio_anio ≠ 1`). El "no" a analizar los valores diarios/mensuales
sin agregar es `docs/decisiones/decision066.md`.

**Recorte de extremos.** El registro se recorta a años completos: las
unidades (meses o días) que sobran en cualquiera de los dos extremos (el
registro casi nunca arranca o termina justo en el mes de inicio) se
descartan, nunca se completan ni interpolan — warning no bloqueante
`CONTRACT_PARTIAL_YEARS_TRIMMED`.

**Regla asimétrica de cobertura (DECISIÓN 065, R2.3).** Los años de los dos
**extremos** siempre exigen 100 % de cobertura — descartar el extremo
parcial es lo que DECISIÓN 057 ya prescribe, y ahí la parcialidad es la
regla. Un año **interior** incompleto se descarta con
`CONTRACT_INCOMPLETE_YEARS_DISCARDED` si su cobertura no alcanza
`cobertura_minima_interior`; si la alcanza pero está por debajo del 100 %,
se acepta y se emite `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` (nivel normal) con
cuántas unidades le faltaron — su máximo está sesgado a la baja y no puede
quedar invisible. Valor provisorio `cobertura_minima_interior = 1.0`
(estricto, `COBERTURA_MINIMA_INTERIOR` en `aggregation.py`) mientras R0.1
espera respuesta de Facundo — con `1.0` el interior también exige 100 % y
`CONTRACT_INCOMPLETE_YEARS_ACCEPTED` no se emite todavía.

**Etiquetado.** Un año que arranca en el mes de inicio del año Y y corre
hasta el mes anterior de Y+1 se etiqueta con Y — el año calendario en que
empieza. Con `mes_inicio_anio = 1` esto degenera exactamente en el año
calendario.

### Gráficos con eje temporal — corregido por DECISIÓN 058
**Corrección 12/08/2026:** esta sección afirmaba que la regla de "dos
versiones" (calendario y con el `mes_inicio_anio` configurado) aplicaba sin
distinción a los tres gráficos con eje temporal, y los daba por bloqueados
por FE-16 (`Etapa1Result` no expone la serie cruda) — ambas afirmaciones
quedaron desactualizadas: `Etapa1Result` ya expone `serie_efectiva`/
`timestamps_efectivos` desde DECISIÓN 057, y la regla de dos versiones tiene
una excepción real. Ver [DECISIÓN 058](../../../docs/decisiones/decision058.md)
para el razonamiento completo.

`Etapa2AjusteChart`/`Etapa2EventosChart` (Bloque C, DECISIÓN 056) **no**
llevan un toggle calendario/hidrológico por gráfico — el criterio de año ya
se fijó como parámetro del análisis (`mes_inicio_anio`, arriba), no es una
opción de presentación aguas abajo.

La regla de "dos versiones" (calendario y con el `mes_inicio_anio`
configurado) aplica a **serie temporal y boxplot mensual** — son
descriptivos, la versión calendario es una vista comparativa legítima. **No
aplica al gráfico de Chow**: Chow corrió sobre `serie_efectiva` (la
agregación con el `mes_inicio_anio` configurado), y su atípico es un punto
de esa serie específica — en la agregación calendario ese punto puede no
existir o valer otra cosa. El gráfico de Chow se dibuja solo sobre la serie
analizada, sin toggle. El toggle, donde aplica, se muestra con carga
mensual **o diaria** (DECISIÓN 065) — con carga anual el criterio de año ya
lo fijó el usuario al armar el archivo, no hay una segunda agregación
posible para comparar. Con carga diaria, el boxplot mensual grafica los
**máximos mensuales** agregados (no los valores mensuales), rotulado
explícitamente como tal.

### PDF de exportación — CU-01
Se genera on-demand, no se almacena en disco.
Contenido varía según lo ejecutado (solo Etapa 1 vs pipeline completo) y el modo (paso a paso vs experto).
En modo paso a paso: incluir fórmulas con valores sustituidos.
En modo experto: resultados directos, sin fórmulas ni explicaciones.

---

## Pendientes que afectan implementación — no asumir

### Con Facundo (distribuciones ante ceros)
Las siguientes distribuciones ante series con ceros en caudal_precipitacion están pendientes de confirmación.
**No asumir comportamiento — preguntar a Octavio antes de implementar:**
- Gamma 3 parámetros
- Exponencial x₀ y β
- Generalizada de Pareto
- Log-Normal 3 parámetros
- Generalizada Exponencial

**DECISIÓN 061 (17/08/2026, `docs/decisiones/decision061.md`) fijó el
default de implementación mientras se espera esta confirmación — no
resuelve la pregunta de arriba, que sigue pendiente tal cual.** De estas
5, solo Generalizada Exponencial/MV bloquea ante cero por necesidad
matemática real (`log(1-e^-λx)` indefinido en x=0); las demás
combinaciones distribución/método calculan igual y emiten
`DIST_ZEROS_TOLERATED`. Detalle en `core-etapa2-implementation.md`.

### Con área de sistemas UCC (deploy)
El CD (deploy automático a producción) está bloqueado hasta confirmar:
- Docker disponible en servidores UCC
- Acceso SSH desde GitHub Actions
- Restricciones de red/firewall — en particular, **acceso saliente para
  registry de imágenes** (Docker Hub o GitHub Container Registry):
  pendiente de consulta a IT, ver `docs/decisiones/decision028.md` — DECISIÓN 028.

**Actualización 18/07/2026:** acceso al servidor de contenedores
confirmado — usuario de dominio vía portal institucional
(portal.ucc.edu.ar). Credenciales gestionadas por IT fuera de este
repositorio, no se documentan acá. Uso previsto: deploy de la versión
estable a `main`, a cargo de Facundo (ver DECISIÓN 028).

### Datos de fixtures de testing
Los datos de las 9 estaciones de la tesis de Facundo para los tests de regresión matemática
están pendientes de confirmación en formato digital.

---

## Scope V1.0 — lo que NO entra

- Bandas de confianza (RF-GEN-O-11): feature candidata, no prioritaria
- Exportación a Google Drive institucional: feature candidata
- Análisis raster: fuera del alcance
- Tests de carga o performance
- Tests end-to-end de UI automatizados (Selenium/Playwright)
- CD automático a producción (bloqueado por infraestructura UCC)

---

## GitHub Flow — branching

```
main           → producción, siempre estable, nunca commit directo
staging        → integración, nunca commit directo
feature/xxx    → funcionalidad nueva, sale de staging, PR hacia staging
fix/xxx        → corrección, sale de staging, PR hacia staging
```

Flujo de tres niveles:
  feature/xxx → staging  (PR, revisión, CI)
  staging → main         (PR, solo cuando staging está estable)

Nunca merge directo de feature a main.
CI corre en cada PR antes del merge. No mergear sin que CI pase.

**SonarCloud** analiza cada PR además de los cuatro jobs de `ci.yml` (Análisis Automático, sin
paso propio en el workflow). Hoy el check **no es required** en el Ruleset — el botón de merge
queda habilitado con el gate en rojo — así que es consultivo de hecho, no bloqueante. Ver
[DECISIÓN 044](../../../docs/decisiones/decision044.md), sección "La pregunta de gobernanza
abierta", para el estado exacto y las opciones pendientes de decisión de Kevin/Octavio.

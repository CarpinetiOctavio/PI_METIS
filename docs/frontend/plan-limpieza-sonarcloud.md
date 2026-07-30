# Plan — Limpieza de SonarCloud dentro del PR B

**Fecha:** 29 de Julio de 2026.
**Origen:** el PR #17 (`feature/frontend-fases0-5` → `staging`) pasó los cuatro jobs de CI pero
falló el quality gate de SonarCloud.
**Destinatario:** la próxima sesión de Claude Code.
**Alcance:** resolver los 61 issues antes de abrir el PR B, y documentar SonarCloud, que hoy no
existe en ninguna parte del repositorio.
**Decisión de Kevin:** limpieza completa de los 61, dentro del PR B (no en un PR aparte).

> **CORRECCIÓN DE PREMISA — 29/07/2026.** La primera versión de este plan decía que el PR #17
> "se mergeó igual" con el gate en rojo. **Era falso: el PR #17 está abierto y sin mergear.** El
> error vino de interpretar "Octavio aceptó el PR" como *mergeado* cuando fue *aprobado*.
> Detectado por la sesión de Claude Code que iba a ejecutar este plan, que verificó la premisa en
> vez de ejecutarla — el comportamiento correcto, y el segundo caso de esta serie después de
> `.claude/launch.json` en la pasada 2. Todo el Bloque X de abajo existe por esta corrección.

---

## 0. Qué falló y qué no

El gate rompió por **dos condiciones**, no por 61:

- **Reliability Rating: C** — requerido A.
- **Security Rating: C** — requerido A.

`New Issues: 61` aparece con **"No conditions set"** — no es condición del gate. Duplicación
(0.0%) y Security Hotspots pasaron. Coverage dice literalmente que no está configurada.

O sea: **6 issues bloquean el gate; los otros 55 son deuda.** El "5h 27min effort" que muestra
Sonar es la suma de los 61, no el costo de aprobar. Se hace igual la limpieza completa porque es
mecánica y porque deja el proyecto presentable ante el tribunal, pero conviene saber cuál es cuál
por si hay que priorizar a mitad de camino.

### ⚠️ Los números de línea de este documento son del PR A

Sonar analizó el estado mergeado del PR A. Las pasadas 2 y 3 —que están en el PR B y todavía no
se subieron— ya movieron varios de esos archivos. Ejemplo concreto: `role="dialog"` que Sonar
reporta en `StreamPage.tsx` L211 hoy está en **L301**.

**Localizá cada issue por contenido, no por número de línea.** Si un issue ya no existe porque
las pasadas 2 o 3 lo resolvieron, anotalo como tal y seguí.

---

## Bloque X — Estado real de las ramas y secuencia de merge

**Leer antes de escribir una sola línea de código.**

### X1 — Dónde van los arreglos: en `fix/frontend-pasada2`, NO en `feature/frontend-fases0-5`

Los issues los reporta Sonar sobre el PR #17, así que el instinto es arreglarlos ahí. **No se
hace.** La rama `feature/frontend-fases0-5` no se toca.

Motivo, medido y no estimado: de los ~21 archivos que tocarían los arreglos de Sonar, **10
también los modifica el PR B**:

```
.github/workflows/ci.yml
frontend/src/auth/AuthProvider.tsx
frontend/src/auth/guards.test.tsx
frontend/src/auth/guards.tsx
frontend/src/mocks/PendingBadge.tsx
frontend/src/routes/config/ConfigPage.tsx
frontend/src/routes/design-events/DesignEventsPage.test.tsx
frontend/src/routes/entry/EntryPage.tsx
frontend/src/routes/results/Etapa1ResultView.tsx
frontend/src/routes/stream/StreamPage.tsx
```

Dos de esos son conflicto línea a línea garantizado:

- **`Etapa1ResultView.tsx`** — el `<th scope="row">` de S2 va exactamente en las filas donde el
  PR B metió `formatNum`.
- **`StreamPage.tsx`** — la pasada 3 lo reestructuró entero (`inert`, refs de foco, handler de
  Escape, `formatNum`), y Sonar pide cambiar ahí el `role="button"` del timeline y el espaciado
  del botón de resultados.

Resolver esos conflictos a mano en el módulo más delicado del frontend es más riesgoso que la
deuda de mergear un PR en rojo: se puede pisar en silencio un arreglo de accesibilidad de la
pasada 3 o uno de Sonar, y los tests no necesariamente lo detectan.

Además, **arreglar en A no ahorra la segunda ronda de Sonar**: el PR B trae ~6.000 líneas que
Sonar nunca vio y va a generar hallazgos propios igual. Arreglar en A sumaría los conflictos sin
quitar la ronda.

### X2 — El PR #17 se mergea en rojo, y eso es una decisión, no un descuido

El check de SonarCloud aparece en el PR pero **no bloquea**: el botón de merge está habilitado
con el gate en rojo. Se mergea sin cambios.

Lo que separa "mergeamos algo roto" de "secuenciamos una limpieza" son cuatro condiciones, y las
cuatro son obligatorias:

1. **El PR B tiene que estar listo y verde antes** de mergear el A. La ventana en rojo se mide en
   horas, no en días.
2. **Nada va a `main` en el medio.** `main` es lo que importa; `staging` es integración y su razón
   de existir es absorber estados intermedios.
3. **Queda registrado en la DECISIÓN 044** con este razonamiento completo.
4. **El PR B sale verde sí o sí.** Ese es el compromiso que hace válida la deuda.

### X3 — Secuencia exacta

```
1. git push -u origin fix/frontend-pasada2     ← AHORA, respaldo. No abre PR.
2. Bloques S → N → R → T → C → D de este plan  ← sobre esa misma rama
3. Verde local: lint + test + build + pytest
4. Avisarle a Octavio / cerrar su revisión pendiente del PR #17
5. Merge del PR #17 con "Create a merge commit"
6. Push de fix/frontend-pasada2 y abrir el PR B
```

El paso 1 es lo primero que hay que hacer: los 33 commits de las pasadas 2 y 3 existen hoy
únicamente en el disco de Kevin. Pushear la rama no abre ningún PR ni dispara nada.

**Paso 5, sin alternativas: "Create a merge commit".** "Squash and merge" y "Rebase and merge"
rompen la ascendencia de `243f327` y harían que el PR B mostrara 63 commits en vez de 33, con las
~5.700 líneas del frontend reapareciendo como cambios de la pasada 2.

---

## Bloque S — Las 2 condiciones del gate (hacer primero)

Si algo sale mal más adelante y hay que cortar, con este bloque el gate ya pasa.

### S1 — Security: `npm ci` sin `--ignore-scripts`

`.github/workflows/ci.yml`, job `frontend`, paso `- run: npm ci`.

```yaml
- run: npm ci --ignore-scripts
  working-directory: frontend
```

**Verificar, no asumir.** El flag desactiva los scripts de postinstall de todas las dependencias.
Vite 5 y Rollup 4 resuelven sus binarios de plataforma por `optionalDependencies` y no por
postinstall, así que debería andar — pero es exactamente el tipo de cambio que aparece roto en
CI. Probalo local antes de commitear:

```bash
cd frontend
rm -rf node_modules
npm ci --ignore-scripts
npm run lint && npm test && npm run build
```

Si algo se rompe, **no revertir sin más**: identificá qué paquete necesitaba su script y
documentá el motivo. Alternativa si no hay salida: dejar `npm ci` y marcar el issue en Sonar como
*Won't fix* con justificación escrita, nunca silenciarlo sin explicación.

### S2 — Reliability: tabla de descriptivos sin encabezados

`frontend/src/routes/results/Etapa1ResultView.tsx` — la tabla dentro de `{result.descriptive && (...)}`.

Es el **único issue tipado `Bug`** de los 61. Hoy son ocho filas de `<td>rótulo</td><td>valor</td>`
sin ningún `<th>`: un lector de pantalla lee "n, 40" sin saber cuál de los dos es el rótulo.

```jsx
<tr>
  <th scope="row">n</th>
  <td className="num">{formatInt(result.descriptive.n)}</td>
</tr>
```

Las ocho filas. Revisar `Etapa1ResultView.css` — si `th` hereda estilo de encabezado de columna
(negrita, centrado, fondo), agregar una regla para `th[scope="row"]` que lo deje alineado a la
izquierda como estaba el `<td>`.

### S3 — Reliability: tres `<label>` que no etiquetan ningún control

`frontend/src/routes/config/ConfigPage.tsx`, tres lugares (verificado en el código actual):

| Dónde | Qué es hoy |
|---|---|
| L93/94 | `<label id="tipo-variable-label">` + `<div role="group" aria-labelledby>` |
| L115/116 | `<label id="modo-label">` + `<div role="group" aria-labelledby>` |
| L140 | `<label>Modo</label>` suelto, en la rama anónima — no rotula absolutamente nada |

Los dos primeros se arreglan con el markup correcto, que además **elimina de paso los dos smells
de `role="group"`** que Sonar reporta por separado:

```jsx
<fieldset className="field">
  <legend>Tipo de variable</legend>
  <div className="seg">
    …los dos botones, sin role ni aria-labelledby…
  </div>
</fieldset>
```

`<fieldset>` + `<legend>` es exactamente el elemento para agrupar controles relacionados bajo un
rótulo; `role="group"` + `aria-labelledby` era una reimplementación manual de lo mismo.

El tercero (L140) no es un rótulo de nada — reemplazar por `<p className="ct">Modo</p>` o el
equivalente que ya use la hoja de estilos.

**Ojo:** `fieldset` trae estilos por defecto del navegador (borde, padding, márgenes del
`legend`). Ajustar el CSS para que las dos pantallas queden visualmente idénticas a como están
hoy. Correr `npm test` — `ConfigPage.test.tsx` consulta por rol y puede necesitar actualización.

### S4 — Reliability: espaciado ambiguo antes de un `<button>`

`frontend/src/routes/stream/StreamPage.tsx`, reportado en L191 del PR A: el botón "Ver
resultados ▸" dentro del banner de análisis completo. Hay texto y JSX adyacentes donde no queda
claro si el espacio en blanco se renderiza o no. Explicitarlo con `{" "}` o reestructurar el
markup.

### Checkpoint

Después de S1-S4, correr todo y confirmar que el gate pasaría:

```bash
cd frontend && npm run lint && npm test && npm run build
```

---

## Bloque N — Roles ARIA a elementos nativos

### N1 — `role="button"` en los pasos del timeline

`StreamPage.tsx` (L142 del PR A): los `<div className={STEP_CLASS[status]} role="button"
tabIndex={0} onClick onKeyDown>` del timeline agrupado.

Reemplazar por `<button type="button">` real. Se eliminan `role`, `tabIndex` y **todo el
`onKeyDown` manual de Enter/Espacio** — un `<button>` nativo ya hace eso. Es menos código y mejor
comportamiento. Ajustar el CSS (`.step`) para neutralizar los estilos por defecto de botón
(`background`, `border`, `font`, `text-align: left`, `width: 100%`).

### N2 — `role="status"` a `<output>`

`AuthVerifyPage.tsx` (L45) y **también `guards.tsx` L9**, que Sonar todavía no vio porque es
código de la pasada 3. Anticipalo: si no, aparece como issue nuevo del PR B.

`<output>` es un elemento con live region implícita. Verificar que el CSS de `.banner` /
`.auth-loading` siga aplicando (`<output>` es `display: inline` por defecto).

### N3 — `role="dialog"` a `<dialog>` — **RECHAZAR, no aplicar**

Sonar pide usar `<dialog>` nativo en el modal de atípico de `StreamPage.tsx`. **No hacerlo.**

`<dialog>.showModal()` cierra con Escape por defecto y no hay forma limpia de desactivarlo sin
interceptar el evento `cancel`. Eso contradice de frente la decisión de producto tomada en M3.2
de la pasada 3: **Escape no cierra el modal ni resuelve ninguna decisión**, porque el backend
queda bloqueado hasta 300s esperando (`session_store`) y "rechazar"/"aceptar" son las dos únicas
decisiones válidas, cada una con su propio código de auditoría
(`TEST_OUTLIER_REJECTED_BY_USER` / `TEST_OUTLIER_ACCEPTED_BY_USER`). Un Escape accidental no puede
convertirse en una decisión estadística registrada.

Además la implementación actual (`inert` sobre el contenedor de fondo, auto-foco al contenedor
del diálogo, restauración de foco al cerrar) ya está construida y cubierta por tres tests de
regresión.

**Marcar el issue en SonarCloud como *Won't fix*, con el motivo escrito en el comentario**, y
dejar constancia en la DECISIÓN 044 (Bloque D). Un issue rechazado con justificación es un
resultado válido; uno silenciado sin explicación, no.

---

## Bloque R — Smells mecánicos

### R1 — `Readonly` en props de componentes (11)

`AuthProvider.tsx` L27 · `guards.tsx` L6 y L15 · `PendingBadge.tsx` L7 · `EntryPage.tsx` L42 y
L107 · `HistoryPage.tsx` L58 · `Etapa1ResultView.tsx` L47 y L90 · `StreamPage.tsx` L65 ·
`ThemeProvider.tsx` L32.

```tsx
export function Etapa1ResultView({ result, modo }: Readonly<{ result: Etapa1Result; modo: Modo }>) {
```

Aplicar el mismo patrón en los once. Revisar si aparece alguno más en componentes que las pasadas
2 y 3 agregaron (`RankingCard` en `RankingPage.tsx`, `AuthLoading` en `guards.tsx`) — Sonar
todavía no los analizó y van a salir como issues nuevos del PR B.

### R2 — `useMemo` en el value de los dos Context (2)

`AuthProvider.tsx` L79 y `ThemeProvider.tsx` L46.

Este no es cosmético: el objeto que se pasa como `value` se recrea en cada render, así que
**todos los consumidores del context re-renderizan aunque nada haya cambiado**. Con
`AuthProvider` eso es cada pantalla de la app.

```tsx
const value = useMemo(
  () => ({ user, isAuthed: user !== null, isLoading, isAnonymous, login, logout, enterAnonymously, refetch }),
  [user, isLoading, isAnonymous, login, logout, enterAnonymously, refetch],
);
return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
```

Las funciones ya están envueltas en `useCallback`, así que las dependencias son estables. Dejar
que el lint de `react-hooks/exhaustive-deps` valide el array; no escribirlo a mano y confiar.

### R3 — `.dataset` en vez de `removeAttribute` (2)

`frontend/vitest.setup.ts` L19 y L20.

```ts
delete document.documentElement.dataset.theme;
```

Correr la suite completa después: ese archivo limpia estado entre tests y un error acá produce
fallos cruzados difíciles de rastrear.

### R4 — Ternarios anidados (2)

`AuthVerifyPage.tsx` L40 y L47. Extraer a variables con nombre antes del `return`, o a una
función auxiliar. Es de los pocos smells donde el resultado se lee genuinamente mejor.

---

## Bloque T — Tests: `findBy*` en vez de `waitFor` + `getBy` (32)

| Archivo | Líneas (del PR A) |
|---|---|
| `App.test.tsx` | 36 |
| `auth/guards.test.tsx` | 44, 55, 70, 81 |
| `routes/auth-verify/AuthVerifyPage.test.tsx` | 38, 59 |
| `routes/config/ConfigPage.test.tsx` | 39, 88, 115 |
| `routes/design-events/DesignEventsPage.test.tsx` | 63, 71, 81, 90, 100 |
| `routes/entry/EntryPage.test.tsx` | 46, 73, 103, 137, 161, 169 |
| `routes/history/HistoryDetailPage.test.tsx` | 60, 67, 74 |
| `routes/history/HistoryPage.test.tsx` | 47, 71 |
| `routes/results/ResultsPage.test.tsx` | 97, 102, 123, 128, 139, 148 |

Transformación:

```ts
// antes
await waitFor(() => expect(screen.getByText("Análisis completo.")).toBeInTheDocument());
// después
expect(await screen.findByText("Análisis completo.")).toBeInTheDocument();
```

**Tres advertencias, porque esto es donde se rompen cosas:**

1. **No es siempre 1:1.** Si un `waitFor` contiene **varias** aserciones, no se puede convertir
   directamente: `findBy*` espera un solo elemento. En ese caso, o se deja el `waitFor` (y se
   marca el issue como *Won't fix* con motivo) o se separa en un `findBy*` para la condición que
   dispara la espera más aserciones sincrónicas después.
2. **`findBy*` falla si hay más de una coincidencia**, igual que `getBy*`. Si el `waitFor`
   original usaba `getAllBy*`, va `findAllBy*`.
3. **Correr `npm test` después de cada archivo, no al final.** Doce archivos y 32 cambios: si
   rompés algo, querés saber cuál fue.

Al terminar el bloque, el conteo debe seguir siendo **126 tests**. Si cambió, se agregó o se
perdió un test sin querer.

---

## Bloque C — Configuración de SonarCloud

### C1 — Crear `sonar-project.properties` en la raíz

Hoy no existe. Como mínimo:

```properties
sonar.projectKey=CarpinetiOctavio_PI_METIS
sonar.organization=<la organización real — confirmarla en SonarCloud, no inventarla>

# Artefactos generados por herramientas — no son código nuestro.
# mockServiceWorker.js lo genera `npx msw init` (ver DECISIÓN 042).
sonar.exclusions=frontend/public/mockServiceWorker.js,frontend/dist/**,frontend/frontend-design/**

sonar.sources=backend/metis,frontend/src
sonar.tests=backend/tests,frontend/src
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx,backend/tests/**
```

Sobre `frontend/frontend-design/`: son los prototipos HTML de diseño, no código de producción.
Excluirlos evita que Sonar los analice como aplicación real. **Confirmá que la exclusión no borre
issues legítimos** antes de darla por buena.

Esto resuelve el issue de `mockServiceWorker.js` L1 ("Specify the rules you want to disable"),
que no se arregla editando un archivo generado.

### C2 — Cobertura: documentarla como pendiente, NO implementarla acá

Sonar avisa que la cobertura no está configurada. Tenés 126 tests de frontend y 131 de backend
sin ningún crédito, y para la defensa la cobertura reportada es un artefacto fuerte.

**Pero no entra en el PR B**, por un motivo técnico concreto: SonarCloud parece estar corriendo
con **análisis automático** (no hay ningún paso de Sonar en `ci.yml` y aun así analiza los PRs).
El análisis automático **no importa reportes de cobertura** — para eso hay que migrar al scanner
corriendo dentro de CI, lo que requiere un `SONAR_TOKEN` como secret del repositorio.

Eso toca secretos y configuración de la organización: es territorio de Kevin y Octavio, no de una
sesión de agente. **Verificá primero si el análisis es automático o por CI** (SonarCloud →
Administration → Analysis Method) y documentá el hallazgo. Si resulta que ya corre por CI, la
cobertura sí se puede cablear y pasa a ser una tarea normal.

---

## Bloque D — Documentación (esto es lo que más importa)

**SonarCloud gobierna si el código entra y no existe en ninguna parte del repositorio.** No está
en `ci.yml`, no está en `.claude/rules/testing.md` —que tiene una sección "Análisis estático
(también obligatorio)" mencionando solo ruff y ESLint—, no está en `constraints.md`, no está en
`CLAUDE.md`. Es la misma clase de hueco que las tres pasadas anteriores vinieron a cerrar.

### D1 — `docs/decisiones/decision044.md`

Reservar el 044 en el índice de `docs/decisiones/README.md` **antes** de escribir contenido
(mismo procedimiento que la pasada 2 con 036-042).

Contenido mínimo:

- **Qué es** SonarCloud en este proyecto, cómo está conectado (App de GitHub / análisis
  automático — confirmar), y qué evalúa el quality gate.
- **Las dos condiciones que fallaron** en el PR #17 y qué las causó.
- **El rechazo explícito de `<dialog>` nativo** (N3), con el razonamiento completo: una
  herramienta de análisis estático no conoce las restricciones de dominio del proyecto, y este es
  el caso donde seguirla habría revertido una decisión de producto tomada a propósito. Es un buen
  ejemplo para el tribunal de criterio de ingeniería sobre automatismo.
- **Cualquier otro issue marcado *Won't fix***, con su motivo.
- **La decisión de mergear el PR #17 en rojo** (X2), con las cuatro condiciones y el dato de los
  10 archivos solapados que la justifica. No alcanza con decir "se decidió"; tiene que quedar el
  razonamiento para que sea auditable.
- **La pregunta de gobernanza abierta** (D3).

### D2 — Actualizar las reglas del repo

- `.claude/rules/testing.md`, sección "Análisis estático (también obligatorio)": agregar
  SonarCloud junto a ruff y ESLint, con qué mide y dónde se ve.
- `.claude/rules/architecture/constraints.md`: sumarlo donde corresponda a las herramientas no
  negociables.
- `CLAUDE.md`: mencionarlo donde se describe CI, para que toda sesión nueva sepa que existe un
  gate más allá de los cuatro jobs de `ci.yml`.

### D3 — Decisión de gobernanza pendiente — **para Kevin y Octavio, no para el agente**

Verificado en la interfaz del PR #17: **el check de SonarCloud no es *required*** (el botón de
merge queda habilitado con el gate en rojo) y **la revisión tampoco lo es** ("Review has been
requested. It is not required to merge"). O sea que hoy el gate es consultivo de hecho.

Eso choca con lo que afirma `.claude/rules/sprint.md`, sección "Estrategia de ramas": que el
Ruleset "bloquea push directo, exige PR + CI". Lo primero es cierto y está verificado; lo segundo
hay que comprobarlo contra la configuración real del Ruleset y corregir la afirmación si no se
sostiene.

Las opciones son: gate bloqueante (required check en el Ruleset), gate consultivo con revisión
obligatoria, o gate consultivo sin más.

Opinión registrada para que la evalúen: conviene hacerlo *required* **una vez que los dos PRs
estén verdes**, no antes — ponerlo ahora bloquearía el propio merge del PR #17 que la secuencia
de X3 necesita.

**No la resuelva el agente.** Registrarla como pregunta abierta en `decision044.md` con estado
PENDIENTE DE DECISIÓN, igual que la 043. Y corregir o verificar la afirmación de `sprint.md`.

---

## Orden de ejecución

```
0. X3 paso 1 (push de respaldo de fix/frontend-pasada2)   ← antes que nada
1. S1 → S2 → S3 → S4        ← el gate ya pasaría acá
2. N1 → N2 → N3(rechazo)    ← roles ARIA
3. R1 → R2 → R3 → R4        ← smells mecánicos
4. T                         ← tests, archivo por archivo
5. C1 → C2                   ← configuración de Sonar
6. D1 → D2 → D3              ← documentación
7. Verificación final
8. X3 pasos 4-6 (aviso a Octavio → merge del PR #17 → PR B)
```

Todo entre el paso 1 y el 7 ocurre sobre `fix/frontend-pasada2`, en local. Commits separados por
bloque, no uno solo de 61 arreglos.

Commits separados por bloque, no uno solo de 61 arreglos.

## Verificación final

Con salida real pegada en el informe:

1. `cd frontend && npm run lint && npm test && npm run build` — verde, **126 tests**. Si el
   número cambió, explicar por qué.
2. `npm ci --ignore-scripts` desde `node_modules` borrado — el build sigue funcionando (S1).
3. `bash ./scripts/check-error-catalog.sh` — las tres direcciones OK.
4. `docker exec <backend> pytest -m unit -v` — 131 passed, 1 skipped.
5. Sweep de enlaces relativos sobre `*.md` — cero rotos (D1 agrega archivos y referencias).
6. Ningún `role="group"`, `role="button"` ni `role="status"` en `frontend/src` — salvo los
   rechazados a propósito y documentados.

## Después: merge del PR #17 y apertura del PR B

Recién con todo lo anterior en verde, ejecutar los pasos 4 a 6 de X3, y después el **paso 8** de
`INSTRUCCIONES-PR-frontend.md`.

**Esperá una segunda ronda de Sonar.** El PR B trae ~6.000 líneas nuevas que Sonar nunca vio
(todo lo de las pasadas 2 y 3, más estos arreglos), así que es probable que aparezcan issues
nuevos en código nuevo: `Readonly` en `RankingCard` y `AuthLoading`, `role="status"` en
`guards.tsx`, y lo que traiga `scripts/check-error-catalog.sh`. Es esperable, no un fracaso —
resolverlos en la misma rama con commits adicionales.

## Nota para el agente

- **Ya detectaste una premisa falsa en este plan** (que el PR #17 estaba mergeado) y hiciste lo
  correcto: verificar antes de ejecutar. Seguí con ese criterio — es el segundo caso de la serie
  y las dos veces el plan estaba equivocado, no el repo.
- Los números de línea son del PR A. **Localizá por contenido.** Si un issue ya no existe porque
  las pasadas 2 o 3 lo resolvieron, anotalo y seguí.
- **No toques `feature/frontend-fases0-5`** bajo ninguna circunstancia (X1).
- Si un arreglo de Sonar contradice una decisión documentada del proyecto, **la decisión gana**:
  se marca *Won't fix* con motivo escrito, no se aplica en silencio. N3 es el precedente.
- Reportá números reales, no esperados. En las tres pasadas anteriores el conteo de commits se
  reportó mal dos veces por estimarlo en vez de correr `git rev-list --count`.

# Plan de mejora del frontend — Pasada 4 (identidad visual, interacción y dos funcionalidades)

**Fecha.** 31 de Julio de 2026.
**Rama sugerida.** `feature/frontend-pasada4`, saliendo de `staging` **una vez mergeada `fix/frontend-ui-integracion`** (ver §1.3 — precondición dura).
**Entradas.** [`informe-resultados-arreglo-ui-rota.md`](./informe-resultados-arreglo-ui-rota.md) (cierre de la pasada anterior) y [`feedback-ux-pendiente-analisis.md`](./feedback-ux-pendiente-analisis.md) (relevamiento sin decidir).
**Qué es este documento.** Un plan ejecutable por un agente, no un relevamiento. Cada ítem tiene archivo, cambio concreto, criterio de aceptación y su cobertura de test. Sigue el formato de [`plan-mejora-frontend-pasada2.md`](./plan-mejora-frontend-pasada2.md) y [`pasada3`](./plan-mejora-frontend-pasada3.md).

**Alcance decidido por Kevin (31/07/2026).** De los cinco puntos del feedback de UX entran **1, 2, 4 y 5(a)**. Quedan fuera, explícitamente: el punto 3 (`tipo_variable` extensible — toca reglas de dominio en `core/`, requiere consulta a Facundo) y el punto 5(b) (búsqueda por nombre de archivo — requiere cambio de esquema previo). Verificación final con **Claude en el navegador**; Playwright y la DECISIÓN 046 siguen diferidos.

---

## 1. Estado de entrada — qué encontré al revisar la pasada anterior

### 1.1 Lo que quedó bien, verificado contra el código

Revisé los 18 commits de `fix/frontend-ui-integracion` contra los archivos reales, no contra el informe. Los arreglos se sostienen:

- **F1** — `StreamPage.tsx` tiene ahora un solo efecto con la limpieza colocada y sin `startedRef`; el `formRef` congela la referencia del primer render. Es exactamente el arreglo correcto, y el comentario inline explica el costo aceptado (doble disparo en dev bajo StrictMode).
- **F7** — `RequireSession` existe en `guards.tsx` y no reintroduce la distinción CU-01/CU-02 por ruta, tal como exige `constraints.md`. El comentario lo argumenta bien.
- **F4/F5/F6** — `TopBar.tsx` tiene links reales, `exitAnonymously()` nuevo, y ambos caminos de salida navegan a `/`.
- **Capa de tests** — `renderPage.tsx`, `StreamPage.lifecycle.test.tsx`, `StreamPage.integration.test.tsx` y `routes.navigation.test.tsx` existen y cubren lo que el plan pedía. 147 tests en 25 archivos.
- **F9** — `frontend/Dockerfile` existe, multi-stage, con `try_files` en su `nginx.conf`.

### 1.2 Observaciones sobre lo que reporta el informe

Tres cosas que vale la pena registrar, ninguna grave:

- **La honestidad sobre las premisas erradas es correcta y está bien fundada.** Los tres ítems de §1 del informe (Cramer ya resuelto, MSW evitado, `FRONTEND_ORIGIN`/`FRONTEND_URL` no eran duplicación) los verifiqué y son ciertos. El agente revisó antes de tocar en vez de aplicar el plan a ciegas — es el comportamiento que corresponde.
- **La desviación de MSW a mock de módulo en la Capa 2 está bien justificada**, pero tiene una consecuencia que el informe no dice: `StreamPage.integration.test.tsx` sigue sin ejercitar el parseo real de frames SSE (`fetchEventSource` mockeado inyecta eventos ya parseados). Un bug en el formato del frame del backend seguiría siendo invisible. No es un defecto de esta pasada — es una limitación conocida que conviene anotar, no arreglar ahora.
- **Los 18 commits en una sola rama sin PR** son el pendiente operativo real. El plan anterior recomendaba tres PRs; se hizo uno solo. Es una decisión a confirmar, pero **nada de esta pasada 4 debería empezar antes de resolverlo** (ver 1.3).

### 1.3 Precondición dura antes de arrancar

`fix/frontend-ui-integracion` no está pusheada ni tiene PR. **Esta pasada 4 no arranca hasta que ese trabajo esté mergeado a `staging`.** Abrir una rama nueva encima de 18 commits locales sin revisar repite exactamente el patrón que produjo la UI rota: apilar trabajo sin verificación intermedia. Pasos previos, en orden:

1. Pushear `fix/frontend-ui-integracion` y abrir PR hacia `staging`. **Hecho — es el PR #19.**
2. Confirmar los cuatro jobs de CI (`lint`, `test`, `error-catalog`, `frontend`) en verde.
3. Resolver el quality gate de SonarCloud del PR #19 — ver 1.4.
4. Mergear.
5. Recién entonces `git checkout -b feature/frontend-pasada4 staging`.

### 1.4 — Bloque 0: quality gate de SonarCloud del PR #19

Tres issues abiertos sobre el PR #19. **Corresponden a ese PR, no a la pasada 4** — arreglarlos ahí, antes de mergear, es lo correcto: son el trabajo de la pasada anterior y arrastrarlos a una rama nueva los convierte en deuda heredada sin dueño. Se documentan acá porque este plan es el punto de retoma vigente, y porque uno de los tres es un falso positivo que conviene dejar explicado antes de que alguien lo "arregle" mal.

Aplica el criterio de la [DECISIÓN 044](../decisiones/decision044.md): SonarCloud es consultivo, no todo lo que marca se acata — el precedente es el rechazo del `<dialog>` nativo. Acá, dos se arreglan y uno se corrige en la causa, no en el síntoma.

#### S1 — `frontend/Dockerfile` L13: nginx corre como root (Vulnerability, Minor)

**Válido, se arregla.** El hallazgo es real: `FROM nginx:alpine` corre el proceso como root, y el contenedor va a desplegarse en la infraestructura de la UCC.

Reemplazar la imagen de la etapa final por `nginxinc/nginx-unprivileged:alpine`, que corre como UID 101 y ya trae los permisos resueltos sobre `/var/cache/nginx` y el pidfile — no hace falta agregar `USER`, `chown` ni `RUN` extra.

Condición que lo hace posible sin más cambios: `frontend/nginx.conf` ya escucha en el **puerto 3000**, que está por encima de 1024. Un usuario sin privilegios no puede bindear puertos privilegiados; si el listen fuera 80, este cambio requeriría además remapear el puerto y tocar `docker-compose.yml` y el `proxy_pass` del reverse proxy. No es el caso.

**Verificación:**
```
docker compose up -d --build frontend
docker compose exec frontend id          # esperado: uid=101(nginx)
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/        # 200
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/config  # 200 (fallback SPA)
```
Confirmar también que la ruta de destino del `COPY` de la configuración (`/etc/nginx/conf.d/default.conf`) sigue siendo la correcta en esa imagen antes de dar el cambio por bueno.

**Nota relacionada, deliberadamente fuera de alcance:** el servicio `nginx` de `docker-compose.yml` (el reverse proxy, `nginx:alpine` en 80/443) también corre como root. SonarCloud no lo ve porque no hay Dockerfile propio para ese servicio. Ahí sí hay puertos privilegiados de por medio, así que no se resuelve con el mismo cambio de una línea. Queda anotado como pendiente de infraestructura, no se fuerza en este PR.

#### S2 — `TopBar.test.tsx` L171: `waitFor` + `getByRole` (Code Smell, Minor)

**Válido, se arregla, y hay precedente directo.** La limpieza de SonarCloud anterior ya hizo esta misma migración en seis archivos (`d611ed8`, `785d657`, `c2ec341`, `81349a3`, `dce20c0`, `eda4e55`). Este caso quedó afuera porque el archivo se modificó después.

```tsx
expect(
  await screen.findByRole("button", { name: "Salir" }),
).toBeInTheDocument();
```

**Importante — no extender el cambio al resto del archivo.** Verifiqué las siete apariciones de `waitFor` en `TopBar.test.tsx`: L171 es la única con `getByRole`; las otras seis (L65, 77, 95, 116, 137, 151) usan `getByTestId` junto a `toHaveTextContent`, y la regla no las cubre **con razón**. Esos tests esperan a que el texto de un nodo *cambie* ("Conectando…" → "Backend conectado"), no a que el nodo *aparezca* — el nodo existe desde el primer render. Convertirlas a `findByTestId` resolvería de inmediato y el test pasaría sin haber verificado nada. Sería debilitar la suite para satisfacer una regla que ni siquiera se está aplicando.

#### S3 — `renderPage.tsx` L4: "Complete the task associated to this TODO comment" (Info)

**Falso positivo. No hay ninguna tarea pendiente.** La línea dice:

```
// Capa 1 de testing (…§4.1): todo test que renderiza una PÁGINA lo hace bajo StrictMode.
```

La regla S1135 busca la palabra `TODO` sin distinguir idioma, y ahí "todo" es español — *every test*, no *to-do*. No hay nada que completar.

**Fix correcto: reescribir el comentario** ("cada test que renderiza una página…"), no marcar el issue como falso positivo desde la interfaz de SonarCloud. La reescritura evita que reaparezca en cada análisis y en cada PR; marcarlo a mano hay que repetirlo para siempre.

**Riesgo sistémico que esto expone:** todo el repositorio está comentado en español, así que la colisión va a repetirse. Hoy hay dos ocurrencias más que Sonar todavía no marcó — `routes.navigation.test.tsx` L8 ("todo el plan") y L170 ("todo el pipeline"). Convención a adoptar y anotar como addendum de la DECISIÓN 044: **en comentarios, preferir "cada" / "todos los" / "la totalidad de" antes que "todo" a secas.** La alternativa —silenciar S1135 vía `sonar.issue.ignore.multicriteria` en `sonar-project.properties`— es peor: apagaría una regla de deuda técnica real en todo el proyecto por un choque de idioma que se resuelve reescribiendo tres comentarios.

#### Verificación del bloque

Los tres arreglos entran en **un solo commit** sobre `fix/frontend-ui-integracion` (`fix(sonar): quality gate del PR #19`). Después: `npx vitest run` y `npm run lint` en verde, la imagen del frontend reconstruida y el stack completo respondiendo, y el quality gate del PR #19 sin issues abiertos.

---

## 2. Hallazgos nuevos — la causa concreta de "se ve muy simple"

El documento de feedback de UX describía el síntoma ("sin animaciones, sin transiciones, TopBar poco cuidada") pero no llegó a la causa. Investigué el tema y son cinco defectos concretos, todos verificados.

### G1 — JetBrains Mono nunca se carga. Nadie vio nunca el tema real.

`tokens.instrumento.css` declara `--f-head`, `--f-body` y `--f-mono` como `"JetBrains Mono", monospace`. Pero:

- `frontend/index.html` no tiene ningún `<link>` a Google Fonts ni a ningún otro proveedor.
- No hay ningún `@font-face` ni `@import` en todo `src/` (`grep -rn "font-face\|@import\|googleapis"` → cero coincidencias fuera de las tres declaraciones de token).
- `package.json` no tiene ningún paquete `@fontsource/*`.

**Todo METIS se está renderizando con el monospace por defecto del navegador** — Courier New en Windows, DejaVu Sans Mono en Linux. La identidad tipográfica de Instrumento, que `metis-prototipo-fase3.md` define como "JetBrains Mono en todo (títulos, cuerpo y números): registro de terminal", no existe en el producto. **Esta es, por lejos, la causa individual más grande de que la aplicación se vea genérica**, y se arregla en un commit.

### G2 — Cero feedback de interacción en todo el design system

En las 415 líneas de `components.css` hay **exactamente una** `transition` (`.prog i`, el ancho de la barra de progreso) y **un solo** `:focus-visible` (`.input`). No tienen `:hover`, `:active` ni `:focus-visible`:

`.b` · `.b-pri` · `.b-sec` · `.seg button` · `.chip` · `.step` · `.link-btn` · `.card` · `.tag`

Los `cursor: pointer` están puestos; el feedback visual que el cursor promete, no. Un botón se ve idéntico antes, durante y después del click. Eso es lo que se percibe como "poco cuidado", más que la ausencia de animaciones grandes.

### G3 — El movimiento que la identidad ya especifica está implementado a medias

`metis-identidad-fase2.md`, Dirección 4 (Instrumento), especifica textualmente: *"Línea de escaneo con glow, cursor que parpadea y contadores que suben hasta clavar el estadístico. Esquinas tipo corchete (HUD) en las tarjetas, badge que pulsa como un 'REC' en vivo, botones con halo de señal. En oscuro suma scanlines tipo CRT y glow neón en las cifras."*

| Elemento especificado | Estado real |
|---|---|
| Esquinas HUD en tarjetas | Implementado (`global.css`, `.card::before/::after`) |
| Scanlines CRT en oscuro | Implementado (`.app-shell::after`) |
| Glow neón en cifras | Implementado (`.num` en oscuro) |
| Badge que pulsa "REC" | CSS implementado (`.badge-live`) — **pero ningún componente lo usa. Es CSS muerto.** |
| Línea de escaneo con glow | **No implementado** |
| Cursor que parpadea | **No implementado** |
| Contadores que suben | **No implementado** |
| Halo de señal en botones | **No implementado** |
| Retícula técnica de fondo | Implementada, pero **estática** (`background-image` de dos gradientes) |

### G4 — El criterio para acotar "agregar animaciones" ya estaba escrito

El documento de feedback de UX se preocupaba, con razón, de que *"agregar animaciones sin acotar es la clase de tarea que se expande indefinidamente"*. Resulta que el alcance ya está definido desde el 20/07/2026: `metis-identidad-fase2.md`, sección **"Principios de movimiento (transversales)"**, fija cuatro reglas:

1. El movimiento comunica estado, no adorna. Cada animación mapea a un evento real del pipeline.
2. Contadores que suben hasta el resultado.
3. Duraciones cortas con easing de salida `cubic-bezier(.2,.7,.2,1)`.
4. Respetar `prefers-reduced-motion`.

**Esas cuatro reglas son el criterio de aceptación de todo el Bloque A y B de este plan.** No hay que inventar un alcance: hay que implementar el que ya se decidió y nunca se ejecutó.

### G5 — `TopBar` es el único componente fuera del design system

`TopBar.tsx` se maquetó con estilos inline (`style={{ display: "flex", ... }}`) y no usa ni una clase de `components.css`. Es literalmente el único componente así en todo `src/`. Por eso desentona con el resto — y desde el Bloque 2.1 de la pasada anterior concentra toda la navegación, así que es lo primero que se mira en cada pantalla.

---

## 3. Bloque A — Fundaciones visuales

Sin esto, todo lo demás se construye sobre una base equivocada. **Va primero, y se verifica en el navegador antes de seguir.**

### A1 — Cargar JetBrains Mono de verdad (G1)

Usar `@fontsource-variable/jetbrains-mono` (paquete npm, no CDN): el proyecto se despliega en la intranet de la UCC, donde no hay garantía de acceso saliente a `fonts.googleapis.com`; además evita una petición de terceros y el FOUT asociado.

- `npm i @fontsource-variable/jetbrains-mono` (si esa variante no estuviera publicada, el fallback es `@fontsource/jetbrains-mono` con los pesos 400/600/700 — **confirmar el nombre real del paquete y la familia que expone antes de escribir el import**, no asumirlo).
- Importarlo una sola vez en `src/main.tsx`, junto a los otros imports de CSS de tema.
- Ajustar `tokens.instrumento.css` para que el nombre de familia coincida exactamente con el que expone el paquete (la variante variable declara `"JetBrains Mono Variable"`, la estática `"JetBrains Mono"`), dejando `monospace` como último fallback.

**Criterio de aceptación:** en DevTools → Computed → `font-family` de un `.h` y de un `.num`, resuelve a JetBrains Mono, no a la fallback. Confirmar con la pestaña Network que el `.woff2` se sirve local, no desde Google.

**Atención al build de Docker:** `frontend/Dockerfile` corre `npm ci --ignore-scripts`; los paquetes de `@fontsource` no necesitan scripts de post-instalación, así que no rompe. Verificar igual reconstruyendo la imagen (§8).

### A2 — Tokens de movimiento

Nuevos tokens en el bloque **`:root[data-theme="instrumento"]`** de `tokens.instrumento.css` — el bloque agnóstico de modo, junto a `--f-head` y `--r-sm`, porque el movimiento no cambia entre claro y oscuro:

```css
--ease-out: cubic-bezier(.2, .7, .2, 1);   /* Fase 2, principio de movimiento 3 */
--t-fast: 120ms;                            /* hover, focus, active */
--t-mid: 220ms;                             /* cambios de estado, toggles */
--t-slow: 420ms;                            /* entradas de pantalla, barras */
```

**No se agregan a `tokens.ts`.** Verifiqué `tokenParity.test.ts`: parsea únicamente valores hexadecimales (`/--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]+)\s*;/`) dentro de los bloques `[data-mode="light"|"dark"]`, y `ThemeTokenSet` es una interfaz de colores. Duraciones y easings no encajan en ninguna de las dos cosas y quedarían fuera de la verificación de paridad igual que `--f-head` y `--r-sm`, que hoy tampoco están cubiertos. Meterlos ahí a la fuerza daría una falsa sensación de cobertura. Si más adelante hace falta cubrir los tokens no-color, es una tarea propia — no se resuelve de costado en este plan.

**Regla de uso, esa sí verificable:** ninguna duración ni easing hardcodeado fuera de este bloque. Se puede chequear con `grep -rn "cubic-bezier\|[0-9]\+ms" frontend/src --include=*.css` y confirmar que solo aparece en `tokens.instrumento.css`.

### A3 — Regla global de `prefers-reduced-motion`

Hoy `global.css` solo desactiva `badge-pulse`. Reemplazar por una regla que cubra todo lo nuevo:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Los fondos animados del Bloque B además **no arrancan su loop** en ese caso (no basta con acelerar la animación: hay que no gastar CPU). Ver B4.

### A4 — Estados de interacción en todo el design system (G2)

En `components.css`, para cada clase interactiva. El vocabulario es el de Instrumento: **halo de señal**, no sombras difusas.

| Clase | `:hover` | `:active` | `:focus-visible` |
|---|---|---|---|
| `.b-pri` | brillo del acento +8 %, halo `0 0 0 3px color-mix(in srgb, var(--acc) 25%, transparent)` | `translateY(1px)`, halo apagado | `outline: 2px solid var(--acc); outline-offset: 2px` |
| `.b-sec` | `border-color: var(--acc)`, `color: var(--acc)` | `translateY(1px)` | ídem |
| `.seg button` | `background: var(--acc-soft)` | — | ídem, `outline-offset: -2px` (vive dentro de un contenedor con `overflow: hidden`) |
| `.chip` | `border-color: var(--acc)` | `scale(.97)` | ídem |
| `.step` (no `aria-disabled`) | `border-color: var(--line-strong)`, esquinas HUD al 100 % de opacidad | — | ídem |
| `.link-btn` | subrayado | — | ídem |
| `.card` | (sin hover — no es interactiva) | — | — |

Todas con `transition: <propiedades> var(--t-fast) var(--ease-out)`. **Nunca transicionar `all`** — enumerar las propiedades.

**Restricción no negociable:** `:hover` no puede ser el único portador de información, y `:focus-visible` tiene que ser visible en ambos modos. Esto se cruza con la [DECISIÓN 043](../decisiones/decision043.md) (contraste WCAG del tema, PENDIENTE DE DECISIÓN): **este plan no la resuelve ni la contradice** — se limita a no empeorarla. Al agregar cada estado, verificar contraste del texto resultante contra su fondo; si un estado nuevo cae por debajo de 4.5:1, no se aplica y se anota en la decisión 043.

### A5 — Micro-interacciones que comunican estado

Aplicando el principio 1 de G4 — cada una mapea a un evento real, ninguna es decorativa:

- **`.badge-live` puesto en uso** (hoy es CSS muerto, G3): mostrarlo en `StreamPage` mientras `fase === "streaming"`, con el texto "en vivo". Es el "REC" que la identidad especifica.
- **Contadores que suben** (principio 2 de G4): componente `<CountUp value={n} />` para estadísticos y valores críticos en `StreamPage` y `Etapa1ResultView`. Duración `--t-slow`, easing `--ease-out`, `prefers-reduced-motion` → salta directo al valor final. **Debe respetar `formatNum`** — anima el número, no rompe el formato.
- **Entrada de pasos del timeline**: cuando llega un `test_result` nuevo, el paso correspondiente hace `fade-up` (`opacity 0→1`, `translateY(6px→0)`) en `--t-mid`.
- **Transición de la pill de estado**: `calculando… → aprobada/warning/crítico` con cross-fade, no salto seco.
- **Barra de progreso**: ya transiciona el `width`; sumarle un highlight que barre en la dirección del avance mientras `fase === "streaming"`.
- **Modal de atípico**: entrada con `scale(.98)→1` + fade del backdrop en `--t-mid`. **No tocar nada del focus trap ni del manejo de Escape** — eso lo cerró M3 de la pasada 3 con tests de regresión; una animación no puede alterar el orden de foco.

**Cobertura:** las animaciones no se testean por su apariencia. Lo que se testea es que **el estado final sea el correcto y accesible**: los tests existentes de `StreamPage` y `Etapa1ResultView` deben seguir pasando sin cambios de aserción. Si un test empieza a necesitar `waitFor` por culpa de una animación, la animación está mal implementada (debe animar la presentación, no demorar la aparición del nodo en el DOM).

---

## 4. Bloque B — Fondos animados

Decisión de Kevin: **dot-field reactivo en la aplicación, grid-scan en la puerta de entrada.** Dos fondos hermanos, mismo vocabulario, distinto protagonismo.

### B1 — Decisión técnica: Canvas 2D, cero dependencias nuevas

Las referencias de reactbits (`pixel-blast`, `grid-distortion`) usan Three.js + postprocessing: ~600 KB adicionales al bundle para un efecto de fondo, en una aplicación que se despliega en intranet universitaria y cuyo `npm run build` corre en CI en cada PR. **No se justifica.**

Se implementa con **Canvas 2D y `requestAnimationFrame`**, sin dependencias. Es perfectamente suficiente para la calidad buscada: un campo de puntos reactivo y un barrido son geometría simple; lo que da calidad es el ajuste fino (densidad, easing, opacidad, respuesta al cursor), no la tecnología.

**Esto debe quedar escrito como `docs/decisiones/decision045.md`** (número libre — 035 y 046 están reservados, 045 no lo usó nadie): "Fondos animados en Canvas 2D sin dependencias, WebGL descartado", con las alternativas evaluadas y el costo en bundle medido. Se escribe **antes** de implementar.

### B2 — `<DotFieldBackground />` — fondo de la aplicación

`frontend/src/theme/backgrounds/DotFieldBackground.tsx`

- Retícula de puntos alineada al paso de 28 px de la grilla técnica que ya existe en `.app-shell` — el fondo animado **refuerza** la retícula actual, no la reemplaza ni compite con ella.
- Cada punto tiene un radio y una opacidad base bajos. El puntero genera una onda: los puntos dentro de un radio de influencia aumentan radio/opacidad y viran hacia `--acc`, con caída suave.
- Deriva lenta de fondo (amplitud muy baja) para que no se vea muerto sin el mouse.
- Colores **leídos de las CSS vars en runtime** (`getComputedStyle(document.documentElement).getPropertyValue("--acc")`), nunca hardcodeados — tiene que responder al toggle claro/oscuro sin remontar.
- Se monta una sola vez en `RootLayout`, detrás del `<main>`, con `position: fixed; inset: 0; z-index: 0; pointer-events: none`. Las tarjetas (`.card`, `--surf`) son opacas y quedan por encima: **el texto nunca se lee sobre el fondo animado.**

### B3 — `<GridScanBackground />` — fondo de la puerta de entrada

`frontend/src/theme/backgrounds/GridScanBackground.tsx`, usado solo en `EntryPage`.

- Misma retícula base, pero el protagonista es un **barrido luminoso** que recorre la pantalla periódicamente (cada ~6 s), iluminando las líneas de la grilla a su paso con una estela que decae. Es la "línea de escaneo con glow" que la identidad Fase 2 especifica y que nunca se implementó (G3).
- Intensidad claramente mayor que B2 — es la primera pantalla, no tiene tablas de datos que proteger.
- Mismo sistema de color por CSS vars, mismo respeto de `prefers-reduced-motion`.

**Por qué son hermanos y no el mismo:** ambos parten de la misma retícula de 28 px y el mismo acento. Cambia el gesto — reactivo y calmo en el trabajo, protagónico y cíclico en la entrada.

### B4 — Guardas obligatorias (las cuatro, no negociables)

Estas cuatro son la diferencia entre un fondo animado y un problema nuevo:

1. **`prefers-reduced-motion` → no se arranca el loop.** Se dibuja un frame estático y se sale. No basta con acelerar la animación.
2. **Cancelar el `requestAnimationFrame` en la limpieza del efecto.** Bajo StrictMode el componente monta dos veces; sin `cancelAnimationFrame` en el cleanup quedan **dos loops corriendo para siempre**. Esto es exactamente la clase de bug de F1. Ver B5.
3. **Pausar cuando la pestaña no está visible** (`document.visibilitychange`) y cuando el canvas sale del viewport. No quemar batería animando algo que nadie ve.
4. **`devicePixelRatio` + `ResizeObserver`.** Sin escalar por DPR el fondo se ve borroso en pantallas HiDPI, que es donde más se nota la falta de calidad.

Además: `aria-hidden="true"` en el canvas, y `getContext("2d")` con guarda de `null` (ver B6).

### B5 — Test de ciclo de vida, obligatorio

`frontend/src/theme/backgrounds/DotFieldBackground.lifecycle.test.tsx`

Mismo patrón que `StreamPage.lifecycle.test.tsx`, que ya existe y funciona. Bajo `<StrictMode>`, con `requestAnimationFrame`/`cancelAnimationFrame` espiados:

```
rAF pedidos − rAF cancelados === 1   (queda exactamente un loop vivo)
al desmontar → 0 loops vivos
con prefers-reduced-motion → 0 llamadas a rAF
```

**Este test no es opcional.** El fondo animado es el lugar más probable de todo el plan para reintroducir una fuga de efecto tipo F1, y esta vez sería silenciosa: la aplicación funcionaría, solo consumiría el doble de CPU. Se escribe **antes** que el componente.

### B6 — jsdom no implementa canvas — aislar antes de que rompa 25 archivos de test

`HTMLCanvasElement.prototype.getContext` devuelve `null` en jsdom y emite un error "Not implemented". Si `RootLayout` monta el fondo sin protección, **todos los tests de página** (que ahora pasan por `renderPage.tsx`) empiezan a ensuciar la salida o a fallar.

Dos medidas, ambas:

- **En el componente:** `const ctx = canvas.getContext("2d"); if (!ctx) return;` — salida limpia, sin animación, sin excepción. Es correcto también fuera del test (navegadores con canvas deshabilitado).
- **En `vitest.setup.ts`:** stub de `getContext` que devuelve un objeto con los métodos usados como `vi.fn()`, para que el camino real del componente se ejercite en el test de B5 en vez de salir por la guarda.

**Verificar antes de dar el bloque por cerrado:** correr `npx vitest run` y confirmar que la salida no tiene ningún "Not implemented: HTMLCanvasElement.prototype.getContext".

### B7 — Presupuesto de rendimiento

Criterios medibles, no impresiones:

- Sin interacción, el fondo no puede pasar de **~2 % de CPU** en un equipo de escritorio normal (medir con el Performance monitor de DevTools).
- El bundle de producción **no crece más de 8 KB gzip** por los dos fondos juntos (comparar `npm run build` antes y después; anotar los dos números en la DECISIÓN 045).
- El fondo **nunca** debe reducir el frame rate del stream SSE en vivo, que es la pantalla que más trabaja. Si compiten, el fondo baja su densidad; el stream manda.

---

## 5. Bloque C — TopBar y pulido de pantallas

### C1 — Rehacer `TopBar` dentro del design system (G5)

- Sacar todos los `style={{...}}` inline; crear `components/TopBar.css` con clases que usen los tokens.
- Estructura: wordmark METIS a la izquierda (clase `.logo`, que ya existe y usa `--f-head`); navegación al centro-derecha; indicadores (estado de backend, tema) agrupados a la derecha con separadores finos.
- **Link activo marcado** con `<NavLink>` de react-router (`aria-current="page"` + estilo de acento). Hoy no hay ninguna indicación de en qué pantalla estás.
- El estado del backend pasa a ser un indicador compacto (punto de color + etiqueta), reusando `.badge-live` cuando está conectado. **El texto tiene que seguir presente** — `TopBar.test.tsx` lo asserta por `data-testid` y por contenido, y el estado no puede comunicarse solo por color (regla de accesibilidad de Fase 2).
- El toggle de tema pasa a ser un control de dos estados con transición, no un botón "Cambiar tema" — pero **conserva un nombre accesible explícito**.

**Cuidado:** `TopBar.test.tsx` y `routes.navigation.test.tsx` dependen de los textos actuales de los links ("Nuevo análisis", "Historial", "Cerrar sesión", "Salir") y de `data-testid="backend-status"` / `"user-email"` / `"mode-badge"`. Si se cambia un texto, se actualiza el test **en el mismo commit** y se justifica en el mensaje.

### C2 — Entrada de pantalla

Transición `fade-up` (`opacity` + `translateY(8px)`) al montar cada ruta, en `--t-slow`, exactamente el tratamiento que `metis-prototipo-fase3.md` describe para el prototipo. Implementado en `RootLayout` alrededor del `<Outlet />`, con `key` en la ruta para que se dispare en cada navegación.

**Restricción:** no puede retrasar la aparición del contenido en el DOM (ver la nota de cobertura de A5).

### C3 — Puerta de entrada

Con `GridScanBackground` detrás (B3), subir el panel de marca: wordmark con el tratamiento de glow que la identidad especifica para oscuro, y **cursor que parpadea** después del wordmark (elemento de G3 no implementado, barato y muy característico). El formulario queda sobre superficie opaca, sin cambios de legibilidad.

---

## 6. Bloque D — ConfigPage: columnas por dropdown (punto 2 del feedback)

### D1 — Decisión de arquitectura: el parseo lo hace el backend

Dos opciones estaban abiertas. **Se elige el endpoint de previsualización**, por una razón que el documento de feedback no llegó a nombrar:

> Si el frontend parseara las cabeceras con una librería JS propia, las columnas que ofrece el dropdown podrían **no coincidir** con las que `pandas.read_excel`/`read_csv` ve realmente en `core/validacion/parser.py`. El usuario elegiría una columna que después el pipeline no encuentra. Un endpoint que reusa el mismo `pandas` garantiza que lo que se ofrece es exactamente lo que se va a leer.

Además el backend ya tiene `pandas==2.2.2` y `openpyxl==3.1.2` en `requirements.txt` — costo cero de dependencias, contra sumar `sheetjs` (~400 KB) al bundle del frontend para leer Excel.

**Requiere DECISIÓN nueva** (`docs/decisiones/decision047.md`, o el número libre que corresponda al momento de escribirla): endpoint nuevo = contrato nuevo, y `api-contracts.md` es fuente única.

### D2 — Backend: `POST /api/v1/analysis/preview-columns`

- `multipart/form-data` con el archivo. Auth: JWT **opcional** (mismo criterio que `/analysis/stream` — sirve a CU-01 y CU-02 por igual).
- Respuesta: `{ "columnas": [{"nombre": "anio", "indice": 0, "muestra": ["1980", "1981", "1982"]}, ...], "filas": 40 }`.
- Reusa `pandas` leyendo **solo las primeras filas** (`nrows`), no el archivo completo — es una previsualización, no un análisis.
- Errores con el catálogo existente: si el archivo no se puede parsear, `PARSE_ERROR` (ya está catalogado). Si no hay ninguna columna utilizable, código nuevo → **al catálogo en el mismo commit** (regla de DECISIÓN 038, verificada por `scripts/check-error-catalog.sh`).
- **Stateless y sin persistencia.** No crea sesión, no toca `session_store`, no escribe en BD.

Extraer la lectura de cabeceras a una función de `core/validacion/parser.py` que ambos caminos usen, para que no haya dos parseos que puedan divergir.

### D3 — Frontend: `ConfigPage`

- Al seleccionar archivo → llamada a `preview-columns` → estado de carga visible en los dos campos.
- "Columna X" y "Columna Y" pasan a ser `<select>` poblados con las columnas reales, mostrando nombre y una muestra de valores para desambiguar.
- **Preselección heurística, no obligatoria:** primera columna que parsee como fecha/año → X; primera numérica que no sea la X → Y. El usuario siempre puede cambiarla.
- **Caminos de error que hay que resolver explícitamente**, no improvisar:
  - Archivo sin cabecera → ofrecer las columnas por índice (`0`, `1`, …), que es un valor válido para `_resolver_columna`.
  - Nombres duplicados → desambiguar con el índice en la etiqueta.
  - La previsualización falla → **degradar a los inputs de texto actuales** con un aviso, nunca bloquear la ejecución del análisis. Es coherente con el principio de negocio "METIS detecta y advierte, no bloquea".
- El contrato de `/analysis/stream` **no cambia**: `columna_x`/`columna_y` siguen viajando como string; el dropdown solo elige mejor el valor.

**Cobertura:** tests de `ConfigPage` para preselección heurística, cambio manual, archivo sin cabecera, y degradación a texto libre ante fallo de la previsualización. El último es el más importante y el más fácil de olvidar.

---

## 7. Bloque E y F — Historial y badge

### E1 — Borrar/archivar análisis (punto 5a)

**Decisión a tomar antes de codear: soft-delete, no borrado real.** Argumento para la decisión escrita: `analyses` es el registro de auditoría de CU-01 — `constraints.md` establece que "toda decisión ante un warning es responsabilidad del usuario y queda registrada en el historial". Un `DELETE` físico destruye esa trazabilidad. Se agrega `archivado_at TIMESTAMP NULL`.

- **Migración Alembic** `004_add_archivado_at_analyses.py` (las tres existentes son `001`-`003`; seguir esa numeración, no el hash autogenerado — precedente de DECISIÓN 027).
- **Endpoint** `POST /api/v1/history/{id}/archive` y su inverso `POST /api/v1/history/{id}/unarchive`. Requieren JWT y verifican pertenencia (`user_id`), igual que `get_analysis_by_id`.
- `GET /api/v1/history/` excluye archivados por defecto; parámetro `?archivados=true` para verlos.
- **Contrato al `api-contracts.md` en el mismo commit.**
- **UI:** acción "Archivar" en cada ítem, con confirmación y **deshacer** durante unos segundos (más barato y más amable que un diálogo modal de confirmación). Filtro para ver archivados.

**No incluye la búsqueda por nombre de archivo** (punto 5b), que sigue fuera de alcance: requiere decidir y migrar la captura de `nombre_archivo` primero.

### F1 — Reescribir el `PendingBadge` (punto 4)

Hoy dice "pendiente · datos de ejemplo", con nota "Etapa 2 no expuesta por API todavía". Es lenguaje interno de desarrollo en una pantalla que va a ver un docente, un alumno y eventualmente el tribunal.

Redacción propuesta, a confirmar: **"Vista previa · datos de demostración"**, con nota expandida *"Esta pantalla muestra un ejemplo de cómo se presentarán los resultados. El análisis de frecuencia todavía no se calcula sobre tus datos."*

Dice lo mismo, en el idioma del usuario, sin mentir sobre el estado. No cambia el comportamiento ni contradice la [DECISIÓN 042](../decisiones/decision042.md) — solo su presentación. Actualizar los tests que asserten el texto actual.

---

## 8. Bloque G — Verificación final con Claude en el navegador

Última etapa, después de que todo lo anterior esté commiteado y con CI en verde. **No es opcional ni ceremonial: es la capa que faltó la vez pasada** y la que habría detectado F1 el mismo día.

### G1 — Preparación

```
docker-compose up -d --build          # los cuatro servicios, incluye el frontend nuevo
./scripts/seed-dev-user.sh            # usuario verificado para el camino CU-01
```

Verificar sobre `http://localhost` (a través de nginx, con el build de producción) **y** sobre `http://localhost:5173` (dev, con StrictMode activo). Los dos: son entornos distintos y el bug de la vez pasada solo existía en uno.

### G2 — Recorrido a verificar

Cada punto, con captura o texto de página como evidencia:

| # | Qué verificar | Qué mirar |
|---|---|---|
| 1 | Tipografía real | Computed `font-family` = JetBrains Mono; `.woff2` servido local en Network |
| 2 | Fondo de la puerta de entrada | Grid-scan visible, barrido cíclico, cursor parpadeando, formulario legible encima |
| 3 | Login real | Con el usuario sembrado → llega a `/config`, TopBar con navegación y link activo marcado |
| 4 | Micro-interacciones | Hover, active y focus por teclado (Tab) en botones, segmentos y chips, en claro **y** oscuro |
| 5 | Toggle de tema | Los dos fondos animados cambian de color sin recargar ni parpadear |
| 6 | ConfigPage | Cargar CSV real → dropdowns poblados con columnas reales, preselección razonable |
| 7 | **Stream completo** | Timeline avanza, badge "en vivo" pulsando, contadores subiendo, llega a "Análisis completo". **Confirmar en Network que no hay `ERR_ABORTED` colgado** — es la regresión de la vez pasada |
| 8 | Atípico | Modal con animación de entrada; foco y Escape se comportan igual que antes (M3) |
| 9 | Resultados → Etapa 2 | "Continuar a Etapa 2" funciona; badge con la redacción nueva |
| 10 | Historial | Lista, archivar con deshacer, filtro de archivados |
| 11 | Cerrar sesión | Redirige a `/`, TopBar vuelve al estado sin sesión |
| 12 | `prefers-reduced-motion` | Emularlo en DevTools (Rendering → Emulate CSS media feature) → sin animaciones y **sin loop de rAF corriendo** (Performance monitor) |
| 13 | Consola | Cero errores y cero warnings de React en todo el recorrido |
| 14 | CPU | Performance monitor en reposo en `/config`: fondo por debajo del presupuesto de B7 |

### G3 — Cierre

- Limpiar el usuario sembrado (`./scripts/clean-dev-user.sh`) y bajar el stack.
- Escribir `informe-resultados-pasada4.md` con la salida real de cada verificación — el mismo formato que los informes de las pasadas 2 y 3.
- **Si algo del recorrido falla, no se cierra la pasada.** Se vuelve al bloque correspondiente.

---

## 9. Decisiones nuevas que este plan requiere

Ninguna se implementa sin el archivo escrito primero. Numeración: 035 y 046 están reservados; usar los libres siguientes y actualizar `docs/decisiones/README.md`.

| Decisión | Tema | Bloqueante de |
|---|---|---|
| 045 | Fondos animados en Canvas 2D; WebGL/Three.js descartado, con costo en bundle medido | Bloque B |
| 047 (o siguiente libre) | Endpoint `preview-columns`: parseo de cabeceras del lado del servidor, no del cliente | Bloque D |
| 048 (o siguiente libre) | Archivado de análisis por soft-delete, no borrado físico, por trazabilidad de auditoría | Bloque E |

Siguen pendientes y **fuera de esta pasada**: 043 (contraste WCAG — este plan no la resuelve, solo no la empeora), 046 (E2E Playwright), y la escotilla SMTP de desarrollo.

---

## 10. Orden de ejecución y división en PRs

**Tres PRs, no uno.** La pasada anterior acumuló 18 commits en una rama sin verificación intermedia; no repetirlo.

| PR | Bloques | Por qué corta acá |
|---|---|---|
| **0 — PR #19 ya abierto** | Bloque 0 (§1.4: S1, S2, S3) | No es un PR nuevo: es el que ya está abierto. Los tres issues de SonarCloud se arreglan **ahí**, en un commit, antes de mergear. Nada de lo de abajo arranca hasta que ese PR esté en `staging`. |
| **1 — Fundaciones visuales** | A1-A5, B1-B7, C1-C3 | Es todo visual, no toca backend ni contratos. Se puede verificar en el navegador de una sola pasada y mergear sin riesgo funcional. |
| **2 — Columnas por dropdown** | D1-D3 | Toca backend, contrato y `api-contracts.md`. Merece revisión propia. |
| **3 — Historial y badge** | E1, F1 | Migración de esquema. Nunca mezclar una migración con trabajo visual. |

El Bloque G (verificación con Claude en el navegador) corre **al cierre de cada PR**, con el subconjunto del recorrido que aplique — no solo al final de los tres.

Dentro del PR 1, el orden interno importa:

1. A1 (tipografía) **y verificar en el navegador antes de seguir.** Es probable que solo con esto ya se vea sustancialmente distinto, y eso cambia cuánto pulido hace falta después.
2. A2, A3 (tokens y reduced-motion) — infraestructura de todo lo demás.
3. A4 (estados de interacción) — el mayor retorno por esfuerzo después de A1.
4. B5 (test de ciclo de vida, en rojo) → B2 → B3 → B4/B6/B7.
5. C1-C3.
6. A5 (micro-interacciones ligadas a eventos del stream) al final: es lo que más depende de que el resto esté asentado.

---

## 11. Riesgos

- **"Agregar animaciones" se expande sin límite.** Mitigación: los cuatro principios de movimiento de Fase 2 (G4) son el criterio de aceptación. Toda animación propuesta que no mapee a un evento real de la aplicación se rechaza, aunque quede linda.
- **El fondo animado compite con la legibilidad.** Mitigación: todo el contenido vive sobre superficies opacas (`--surf`), el canvas es `pointer-events: none` y `aria-hidden`. Verificar en G2 punto 2 y 4, en ambos modos. Si en algún caso el texto queda sobre el fondo, es un defecto del layout, no del fondo.
- **Fuga de `requestAnimationFrame` bajo StrictMode.** Es la reincidencia más probable de la clase de bug F1, y esta vez sería silenciosa. Mitigación: B5 escrito antes que el componente, y verificación de CPU en G2 punto 14.
- **jsdom rompiendo la suite entera.** Mitigación: B6, con verificación explícita de que la salida de `vitest` no tiene el warning de `getContext`.
- **`preview-columns` divergiendo del parseo real.** Mitigación: función compartida en `core/validacion/parser.py`, no dos lecturas paralelas.
- **La migración de E1 corriendo contra una BD con datos.** Mitigación: `archivado_at` es nullable sin default — la migración es aditiva y reversible. Probar `alembic upgrade head` y `downgrade -1` contra la BD de Docker antes de commitear.
- **Los tests existentes atados a textos que este plan cambia** (`TopBar`, `PendingBadge`). Mitigación: actualizar test y código en el mismo commit, y justificar el cambio de texto en el mensaje — nunca "arreglar" el test aparte.

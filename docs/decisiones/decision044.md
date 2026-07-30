# DECISIÓN 044 — SonarCloud: quality gate, limpieza del PR #17/B, rechazo de `<dialog>` nativo, merge del PR #17 en rojo

**Fecha:** 30 de Julio de 2026.
**Estado:** Aplicada — limpieza de código completa. Gate de gobernanza (D3) **PENDIENTE DE
DECISIÓN — Kevin/Octavio**.

## Qué es SonarCloud en este proyecto

Análisis estático de terceros sobre `carpinetioctavio/PI_METIS` (`projectKey`
`CarpinetiOctavio_PI_METIS`, organización `carpinetioctavio`), corriendo contra cada PR además de
los cuatro jobs de `ci.yml`. No estaba documentado en ninguna parte del repositorio hasta esta
decisión — el mismo tipo de hueco que decisiones anteriores (036-042) vinieron a cerrar para otras
piezas del frontend.

**Cómo está conectado — verificado, no asumido.** `ci.yml` no tiene ningún paso de Sonar (`grep
-rli sonar .github/workflows/` no matchea nada) y sin embargo el proyecto tiene análisis
corriendo. Verificado vía la API pública de SonarCloud (sin credenciales — no hay acceso a
Administration → Analysis Method):

- `api/components/show?component=CarpinetiOctavio_PI_METIS` → confirma `organization:
  "carpinetioctavio"`, `visibility: "public"`.
- `api/project_analyses/search` → **un solo análisis registrado**, `2026-07-30T05:04:29Z`.
- `api/ce/component` → esa tarea es `type: "REPORT"`, `pullRequest: "17"`, `hasScannerContext:
  true`, `status: "SUCCESS"`.

Un análisis con contexto de scanner y sin ningún paso de CI que lo dispare es la firma de
**Análisis Automático** (App de GitHub de SonarCloud, corre en la nube de Sonar sin necesitar
`SONAR_TOKEN` ni wiring en `ci.yml`). Esto es una inferencia fuerte a partir de evidencia
verificada, no una confirmación directa de la pantalla de Administration — nadie de esta sesión
tiene login en la organización de SonarCloud. Si Kevin/Octavio confirman lo contrario desde la
UI, corregir este párrafo.

Consecuencia práctica (C2 del plan de limpieza): el Análisis Automático **no importa reportes de
cobertura**. Hay 126 tests de frontend y 131 de backend sin ningún crédito en Sonar. Cablear
cobertura requeriría migrar al scanner corriendo dentro de `ci.yml`, lo que exige un `SONAR_TOKEN`
como secret del repositorio — territorio de Kevin/Octavio, no de una sesión de agente. Queda fuera
de esta decisión, documentado como pendiente.

## Las dos condiciones que fallaron en el PR #17

El quality gate no rompió por los 61 issues que Sonar reportó — rompió por dos condiciones
configuradas en el gate:

- **Reliability Rating: C** (requerido A).
- **Security Rating: C** (requerido A).

`New Issues: 61` aparece en el gate con **"No conditions set"** — no es en sí una condición que
bloquee. Duplicación (0.0%) y Security Hotspots pasaron.

De los 61, **6 issues son los que efectivamente bloquean** las dos condiciones de arriba; los
otros 55 son deuda que no impide el gate pero se limpió igual, dentro del mismo PR B, porque es
mecánica y deja el proyecto presentable ante el tribunal:

| Issue | Categoría | Archivo |
|---|---|---|
| `npm ci` sin `--ignore-scripts` | Security | `.github/workflows/ci.yml` |
| Tabla de descriptivos sin `<th>` (único issue tipo `Bug`) | Reliability | `Etapa1ResultView.tsx` |
| `<label>` sin control asociado (×3: dos `role="group"`, un `<label>` suelto) | Reliability | `ConfigPage.tsx` |
| Espaciado ambiguo antes de un `<button>` | Reliability | `StreamPage.tsx` |

Los 55 restantes: roles ARIA reemplazables por elementos nativos (`role="button"`,
`role="status"`), *code smells* mecánicos (`Readonly<>` en props, `useMemo` en `value` de
Context, `dataset` en vez de `removeAttribute`, ternarias anidadas), y 32 conversiones de
`waitFor(() => expect(getBy...))` a `findBy*` en tests.

## El rechazo explícito de `<dialog>` nativo (N3)

Sonar pide reemplazar el `role="dialog"` del modal de decisión ante atípico de Chow
(`StreamPage.tsx`) por el elemento nativo `<dialog>`. **Se rechaza, no se aplica.**

`<dialog>.showModal()` cierra el diálogo con Escape por defecto, sin ninguna forma limpia de
desactivar ese comportamiento sin reimplementar el manejo de foco a mano — lo que anula la ventaja
misma de usar el elemento nativo. Y cerrar con Escape es exactamente lo que **M3 (pasada 3)**
decidió que este modal **no puede hacer**: el backend queda bloqueado hasta 300s
(`session_store`) esperando una de dos decisiones válidas
(`TEST_OUTLIER_REJECTED_BY_USER`/`TEST_OUTLIER_ACCEPTED_BY_USER`), cada una con su propio código
de auditoría — un Escape accidental no puede convertirse silenciosamente en ninguna de las dos.

Es el ejemplo claro de que una herramienta de análisis estático no conoce las restricciones de
dominio del proyecto: seguirla a ciegas acá habría revertido, en silencio, una decisión de
producto tomada a propósito una pasada antes. Marcado como *Won't fix* en SonarCloud con este
mismo motivo (acción pendiente de quien tenga acceso a la organización — esta sesión no tiene
login en SonarCloud para marcarlo desde la UI).

No se identificó ningún otro issue de los 61 que ameritara *Won't fix* — todo lo demás (S, N1,
N2, R1-R4, T) se aplicó tal como Sonar lo señala.

## La decisión de mergear el PR #17 en rojo (X2)

El check de SonarCloud en el PR #17 (`feature/frontend-fases0-5` → `staging`) **no es un check
requerido** — el botón de merge queda habilitado con el gate en rojo — y se mergeó sin volver a
tocar esa rama.

El motivo por el que los arreglos de Sonar no se hicieron directamente sobre
`feature/frontend-fases0-5` (donde Sonar los reportó) es medido, no estimado: de los ~21 archivos
que tocarían los 61 arreglos, **10 los modifica también `fix/frontend-pasada2`** (el PR B, con las
pasadas 2 y 3 ya encima):

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

Dos de esos son conflicto línea a línea garantizado: `Etapa1ResultView.tsx` (el `<th scope="row">`
de S2 cae exactamente en las filas donde el PR B metió formateo de números) y `StreamPage.tsx` (la
pasada 3 reestructuró el módulo entero — `inert`, refs de foco, handler de Escape — y ahí mismo
Sonar pide tocar el timeline y el espaciado del botón de resultados). Resolver eso a mano en el
módulo más delicado del frontend es más riesgoso que la deuda de un PR en rojo: se puede pisar en
silencio un arreglo de accesibilidad de la pasada 3, o uno de Sonar, sin que los tests
necesariamente lo detecten. Arreglar en el PR A tampoco ahorra una segunda ronda de Sonar — el PR
B trae ~6.000 líneas que Sonar nunca analizó y va a generar hallazgos propios sobre código nuevo
sin importar dónde se arregle esto.

Lo que separa "mergeamos algo roto" de "secuenciamos una limpieza deliberada" son cuatro
condiciones, las cuatro obligatorias:

1. El PR B tiene que estar listo y verde **antes** de mergear el A — la ventana en rojo se mide en
   horas, no en días.
2. Nada va a `main` en el medio — `main` es lo que importa, `staging` es integración y existe para
   absorber estados intermedios como este.
3. Queda registrado acá, con el razonamiento completo.
4. El PR B sale verde sí o sí — es el compromiso que hace válida la deuda.

## La pregunta de gobernanza abierta (D3)

Verificado en la interfaz del PR #17: **el check de SonarCloud no es *required*** (el botón de
merge queda habilitado con el gate en rojo) y **la revisión tampoco lo es** ("Review has been
requested. It is not required to merge"). Hoy el gate es consultivo de hecho, no bloqueante.

Esto contradice lo que decía `.claude/rules/sprint.md`, sección "Estrategia de ramas": que el
Ruleset de protección de ramas "bloquea push directo, exige PR + CI". La primera mitad es cierta y
está verificada (push directo a `staging`/`main` está bloqueado); la segunda —que exige CI para
mergear— no se sostiene tal como está escrita, al menos para el check de SonarCloud. Corregido en
`sprint.md` en el mismo commit que esta decisión.

**Estado: PENDIENTE DE DECISIÓN — Kevin/Octavio, no de esta sesión**, igual que la
[DECISIÓN 043](decision043.md). Opciones:

1. Gate bloqueante — marcar el check de SonarCloud como *required* en el Ruleset.
2. Gate consultivo con revisión obligatoria.
3. Gate consultivo sin más (estado actual).

Opinión registrada para que la evalúen, no una decisión tomada: conviene volverlo *required* una
vez que el PR #17 y el PR B estén los dos verdes, no antes — activarlo ahora bloquearía el propio
merge del PR #17 que esta misma secuencia necesita.

## Criterio de hecho

- `decision044.md` existe e indexada en `docs/decisiones/README.md`.
- `sonar-project.properties` existe en la raíz, con `organization=carpinetioctavio` verificado
  contra la API pública de SonarCloud, no inventado.
- Las 6 condiciones bloqueantes del gate (S1-S4) están corregidas y verificadas localmente
  (`npm run lint && npm test && npm run build`, 126 tests).
- Los 55 issues de deuda restantes (N1-N2, R1-R4, T) están corregidos; N3 documentado como
  *Won't fix* acá arriba.
- `.claude/rules/testing.md`, `.claude/rules/architecture/constraints.md` y `CLAUDE.md` mencionan
  SonarCloud (D2).
- `.claude/rules/sprint.md` corregido: ya no afirma que el Ruleset "exige... CI" sin matiz.

**Ver también:** [DECISIÓN 038](decision038.md) y [DECISIÓN 039](decision039.md) — mismo patrón de
"esto no estaba documentado en ningún lado" que esta decisión cierra para SonarCloud;
[DECISIÓN 043](decision043.md) — precedente de hallazgo con estado PENDIENTE DE DECISIÓN para
Kevin/Octavio.

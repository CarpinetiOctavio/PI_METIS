# DECISIÓN 046: E2E automatizados con Playwright contra el sistema desplegado; sale de `constraints.md` la exclusión de E2E de UI

**Fecha:** 8 de octubre de 2026
**Estado:** Decidida — implementación en el Bloque B6 de `docs/plan-tp-calidad-software.md`.
**Decide:** Kevin.
**Origen:** número reservado el 31/07/2026 por `docs/historico/planes/frontend/plan-arreglo-ui-rota.md` §4.3 para
"escribir primero la revisión de la exclusión" antes de sumar Playwright. Se escribe ahora porque se dan las dos
condiciones que faltaban: Etapa 2 está cableada de punta a punta y el TP integrador de Calidad de Software exige un
flujo E2E automatizado en cada despliegue.

### Contexto

**De dónde sale la exclusión.** `constraints.md`, sección "Scope V1.0 — lo que NO entra", lista "Tests end-to-end
de UI automatizados (Selenium/Playwright)" desde el commit `6d2df20` (05/05/2026), que crea el archivo completo
dentro del PR #2 (`feature/db-models`). El mensaje del commit solo habla del GitHub Flow; la lista de alcance entró
en el mismo archivo sin mención, y el archivo se movió a `.claude/rules/architecture/` en el PR #15 sin tocar esas
líneas. **El repo no registra ninguna justificación**: no hay una decisión que excluya los E2E, solo la línea en la
lista, al lado de recortes como bandas de confianza, raster y el CD a la UCC.

**Por qué estaba ahí (explicación de Kevin, 08/10/2026).** Cuando se escribió, el proyecto era solo backend:
todavía no había frontend sobre el cual correr un E2E de UI. "No hay E2E de UI" describía ese momento y quedó
escrito como si fuera una restricción del proyecto; a lo largo del desarrollo se leyó como regla. Esta decisión
revisa un recorte de alcance de la fase solo backend que nunca se justificó, no revierte una decisión fundamentada.

**Por qué hace falta.** El informe `docs/historico/planes/frontend/informe-diagnostico-ui-rota.md` registró que dos
PR de frontend se mergearon con CI verde y 98 tests en verde con la aplicación rota. Cinco de esos defectos solo eran
detectables con el sistema completo corriendo:

| Defecto | Qué pasaba | Por qué ningún test unitario lo veía |
|---|---|---|
| F1 | El stream se abortaba a sí mismo al montar, bajo StrictMode | Los tests no montaban la app en StrictMode |
| F4 | Ninguna pantalla navegaba a `/history` | Cada pantalla se probaba sola, con rutas armadas por archivo |
| F5 | Etapa 2 inalcanzable | Ídem |
| F6 | "Cerrar sesión" no redirigía | El efecto dependía de la navegación real |
| F9 | `frontend/Dockerfile` no existía | Nadie levantaba el compose completo |

Las capas 1 y 2 de `testing.md` (StrictMode por regla, navegación sobre el array `routes` real) cerraron parte del
hueco. La capa 3 (E2E) quedó pendiente de esta decisión, y la verificación manual con capturas (capa 4, C1a de
`plan-post-pasada4-roadmap.md`) la reemplazó mientras tanto. La verificación manual no corre en cada despliegue.

### Decisión

1. **Se agregan E2E automatizados con Playwright** (`@playwright/test`, versión exacta, solo Chromium) en
   `frontend/e2e/`. Los mantiene Kevin, autor de la mayor parte del frontend.
2. **Corren contra el build de producción servido por nginx**, en el despliegue efímero del pipeline (Docker Compose
   dentro del runner de GitHub Actions) y en el despliegue local de la demo. Nunca contra `npm run dev`: en desarrollo
   StrictMode monta dos veces (`AuthVerifyPage` verifica el token dos veces, `StreamPage` abre dos streams) y el
   resultado no representa lo que ve el usuario.
3. **Alcance chico y deliberado:** seis escenarios sobre los flujos críticos, no la UI entera. Registro con mail real
   capturado por Mailpit (DECISIÓN 049), login, análisis completo de CU-01 con la pausa de Chow y la de Etapa 2 y la
   exportación PDF, historial, CU-02 anónimo y el bloqueante de serie corta. El detalle (selectores, fixtures,
   trampas) está en el Bloque B6 del plan.
4. **En CI corren solo en PR a `staging` y `main`**, no en cada push, y el reporte HTML se sube como artefacto
   siempre, también en verde: es la evidencia automática de la capa 4.
5. **Sale de `constraints.md`** la línea "Tests end-to-end de UI automatizados (Selenium/Playwright)", con referencia
   a esta decisión. La línea de pruebas de carga sale por DECISIÓN 077.

### Alternativas evaluadas

- **Mantener la exclusión y seguir con verificación manual (C1a).** Descartada: no corre en cada despliegue, depende
  de que alguien se acuerde, y ya falló una vez (`c27d6ac` rompió el stream después de una verificación manual que lo
  daba por bueno).
- **Cypress.** Descartada: Playwright maneja descargas (`waitForEvent("download")`, necesario para el PDF que se baja
  con `<a download>` sobre un blob) y varias pestañas sin plugins, trae trazas y video de serie y corre en el mismo
  Node que ya usa el frontend. Cypress no aporta nada que este alcance necesite.
- **Selenium.** Descartada: más infraestructura (drivers, grid) para el mismo resultado, y sin las esperas
  automáticas que evitan los `sleep` frágiles.
- **E2E de la UI entera.** Descartada: el costo de mantenimiento crece con cada pantalla y la mayor parte de la UI ya
  está cubierta por las capas 1 y 2. Se automatiza lo que solo el sistema completo puede romper.

### Consecuencias

- El job de CI se alarga (despliegue + navegador). Se mitiga corriéndolo solo en PR a `staging`/`main`.
- Los E2E son más frágiles que los unitarios: dependen de nombres accesibles y del tiempo de Etapa 2. Se prefieren
  `getByRole`/`getByLabel` sobre clases CSS y se usa un `expect.timeout` amplio.
- Vitest tiene que excluir `e2e/**`: su `include` por defecto toma `*.spec.ts` y correría los specs de Playwright
  con jsdom.
- `testing.md`, "Capa 3", pasa de "no implementada, requiere decisión" a apuntar a esta decisión.

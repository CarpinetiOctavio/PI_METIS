# Informe de Resultados — Pasada 3 de Mejora sobre el Frontend (cierre)

**Fecha.** 29 de Julio de 2026.
**Alcance ejecutado.** `docs/frontend/plan-mejora-frontend-pasada3.md` — Bloque V (verificación),
Bloque F (F1-F5), Bloque M (M1-M3). Bloque G (merge a `staging`) **diferido, ver §2.**
**Rama.** `fix/frontend-pasada2` (misma rama de la pasada 2 — el merge a `staging` no se hizo
todavía, ver más abajo). 15 commits nuevos sobre los 22 de cierre de pasada 2.
**Propósito de este documento.** Punto único de retoma de esta pasada, mismo formato que
[`informe-pasada2-resultados.md`](./informe-pasada2-resultados.md).

---

## 0. Resultado por ítem

Ninguno omitido.

### Bloque V — Verificación

| # | Estado | Resultado |
|---|---|---|
| V1 | Hecho | `npm run lint && npm test && npm run build` corridos de verdad. Lint limpio, **123/123 tests** (antes de M3), build limpio. Confirma que el informe de pasada 2 no cerró sobre una afirmación falsa. |
| V2 | Hecho | `pytest -m unit` corrido por primera vez de punta a punta vía Docker (`docker-compose up -d backend postgres`, contenedor real `pi_metis-backend-1`). **131 passed, 1 skipped.** `ruff check`/`ruff format --check` también verificados dentro del contenedor, ambos limpios. `CLAUDE.md` actualizado con el procedimiento — ya no asume que el host tiene las dependencias. |

### Bloque F — Gaps encontrados en la revisión

| # | Estado | Resultado |
|---|---|---|
| F1 | Hecho | Regex limpio confirmó: backend→catálogo sin gaps (A3 genuinamente cerrado); catálogo→frontend solo `DIST_*` (esperado). La dirección que faltaba (frontend→catálogo) sí tenía un gap real: `STREAM_CONNECTION_ERROR` y `VALIDATION_ERROR` — códigos que el frontend inventa para condiciones client-side, sin contraparte en `core/`/`services/`. Sección nueva "Códigos originados en el frontend" en `api-contracts.md`; addendum fechado en `decision038.md` con la regla ahora explícitamente bidireccional. Verificado con evidencia real, no solo el comando pegado: la primera corrida del regex corregido *seguía* marcando ambos códigos como faltantes hasta agregar los prefijos `VALIDATION`/`STREAM` a la lista — encontrado y corregido antes de cerrar el ítem, no asumido en verde. |
| F2 | Hecho | `DesignEventsPage.tsx` (valor grande del evento de diseño) y `RankingPage.tsx` (`EEA {item.eea}` crudo) ahora usan `formatNum`. Tests que asertaban los valores crudos (`"312.7"`, `"290.9"`) actualizados al formato real. |
| F3 | Hecho | `architecture.md` — corregida la afirmación de que el frontend "entra en operación recién en la primera instancia de avance del proyecto"; header "Última actualización" actualizado según la convención propia del archivo. Nota moot removida de `CLAUDE.md`. |
| F4 | Hecho | `DECIMALS` 4→5 en `format.ts`, decisión de Kevin — criterio ahora es la precisión con la que la tesis de Facundo imprime sus valores de referencia (`formulas-etapa1.md` §6), no la tolerancia interna de los tests de regresión del backend. Docstring reescrito citando los valores concretos. Limitación de relleno de ceros para valores muy chicos documentada como aceptada, no resuelta. |
| F5 | Hecho | `informe-pasada2-resultados.md`: "18 commits" → "22 commits" (con la corrección anotada, no solo reemplazada). `ConfigPage.tsx`: cita de `metis-wireframes-fase1-decisiones.md` ahora con ruta completa (`frontend/frontend-design/...`), resoluble desde que `frontend-design/` está trackeado. |

### Bloque M — Mejoras

| # | Estado | Resultado |
|---|---|---|
| M1 | Hecho | Auditoría de contraste WCAG (metodología, 2 hallazgos, tabla de propuesta calculada) movida de `sprint.md` a [`decision043.md`](../decisiones/decision043.md) — DECISIÓN 043, número reservado antes de escribir contenido. Estado explícito **PENDIENTE DE DECISIÓN — Kevin/Octavio**. `tokens.instrumento.css` sin tocar. `sprint.md` reducido a una referencia de una línea. |
| M2 | Hecho | `scripts/check-error-catalog.sh` (ejecutable, no solo un snippet documentado) + `scripts/error-catalog-allowlist.txt` (excepciones conocidas, comentadas, versionadas). Job nuevo `error-catalog` en `.github/workflows/ci.yml`, independiente de `lint`. Verificado **en las dos direcciones posibles antes de wirearlo a CI**: corre limpio contra el repo real, y fallar con exit 1 cuando se inyecta a propósito un código no catalogado (probado con una inyección real y revertida, no un supuesto). Documentado como addendum en `decision038.md`. |
| M3 | Hecho | Modal de atípico (`StreamPage.tsx`): auto-foco al contenedor del diálogo al abrir, Escape que ni cierra ni decide (ver §3), restauración de foco al cerrar. Tres tests de regresión nuevos. `sprint.md` actualizado: Fase 6 completa salvo DECISIÓN 043 (que es una decisión de diseño pendiente, no una implementación faltante). |

### Bloque G — Merge a `staging`

| # | Estado | Resultado |
|---|---|---|
| G1 | **Diferido — decisión de Kevin.** | `gh` CLI no está instalado en esta máquina (confirmado en bash y PowerShell) y no hay `GH_TOKEN`/`GITHUB_TOKEN` en el entorno — no se pudo crear ni mergear el PR mediante el flujo estándar. Consultado a Kevin en el momento: eligió **posponer el merge y seguir con el resto del plan primero** en vez de instalar `gh` ahora o empujar la rama para que él abra el PR a mano. `fix/frontend-pasada2` sigue sin pushear a `origin` — ver §2 para el estado y los pasos que faltan. |
| G2 | **No hecho — depende de G1.** | No tiene sentido crear `fix/frontend-pasada3` hasta que G1 mergee la pasada 2 a `staging` (si no, la pasada 3 seguiría apilada sobre la 2 sin re-basear). Todo el trabajo de esta pasada quedó, por decisión explícita, sobre la misma rama `fix/frontend-pasada2`. |

**Números de decisión:** 043 coincide con la propuesta del plan (única decisión nueva de esta
pasada).

---

## 1. Premisas del plan que resultaron incorrectas o necesitaron ajuste

- **Ninguna premisa de fondo del plan resultó falsa** — a diferencia de la pasada 2 con
  `.claude/launch.json`, el plan de pasada 3 no afirmó nada sobre el repo o el código que se haya
  verificado como incorrecto.
- **Gap de entorno no anticipado por el plan:** el plan asume que crear un PR es un paso mecánico
  (`gh pr create` o equivalente). En esta máquina no hay `gh` CLI instalado ni token de GitHub en
  el entorno — el plan no lo contempla como bloqueo posible. Resuelto consultando a Kevin en vez de
  buscar un rodeo (push directo a `staging` hubiera violado `constraints.md` y probablemente
  chocado con el GitHub Ruleset que protege la rama).
- **El regex "limpio" de F1, tal como estaba escrito en el plan, todavía tenía un gap.** El plan
  daba el comando con la lista de prefijos `AUTH|CONTRACT|TEST|DIST|PARSE|SESSION` — corrida tal
  cual, esa lista **no** incluye `VALIDATION`/`STREAM`, así que seguía reportando
  `STREAM_CONNECTION_ERROR`/`VALIDATION_ERROR` como faltantes del catálogo aun después de
  agregarlos a `api-contracts.md`. Encontrado ejecutando el comando de verdad, no copiándolo sin
  correr — corregido agregando los dos prefijos a la lista, documentado en el addendum de
  `decision038.md`.

## 2. Estado real para retomar — importante

**`fix/frontend-pasada2` no está mergeada a `staging` ni pusheada a `origin`.** Todo el trabajo de
las pasadas 2 y 3 (37 commits en total) vive únicamente en el checkout local de esta máquina.
Antes de que cualquier otra persona o sesión pueda ver este trabajo:

1. Resolver el acceso a GitHub (instalar `gh` + `gh auth login`, o configurar un token, o pushear
   la rama para que Kevin abra el PR manualmente — las tres opciones que se le presentaron).
2. Abrir el PR `fix/frontend-pasada2` → `staging`, confirmar que los tres jobs de CI (`lint`,
   `test`, `error-catalog` — nuevo en esta pasada — y `frontend`) pasan.
3. Prestar atención especial al primer merge con `.gitattributes` activo — si aparece una
   renormalización masiva de line endings, parar y avisar antes de mergear (ver G1 del plan).
4. Recién ahí crear `fix/frontend-pasada3` (o renombrar la rama actual, si se prefiere no partir
   la serie) para cualquier trabajo posterior.

## 3. Semántica de Escape en el modal de atípico (M3.2)

**Resuelto: Escape no cierra el modal ni resuelve ninguna decisión.** Solo devuelve el foco al
contenedor del diálogo — el modal queda abierto, sin cambios de estado.

**Por qué.** El backend pausa el pipeline hasta 300s esperando la decisión (`session_store`) — no
hay ningún estado "cancelado" al que volver, y el pipeline no continúa sin una respuesta real.
"Rechazar" y "Aceptar" no son un par decisión/cancelación: son las **dos** decisiones válidas,
cada una registrada en el historial de auditoría de CU-01 con su propio código
(`TEST_OUTLIER_REJECTED_BY_USER` / `TEST_OUTLIER_ACCEPTED_BY_USER` — ver `api-contracts.md`).
Mapear Escape a cualquiera de las dos habría convertido una tecla que mucha gente presiona por
reflejo en una decisión estadística real, registrada como si el usuario la hubiera elegido a
propósito. La opción que sí es segura ante un Escape accidental es no hacer nada — el usuario
sigue viendo el modal y tiene que elegir un botón explícitamente.

Por el mismo motivo, el auto-foco al abrir tampoco cae en ninguno de los dos botones (que
convertiría un Enter apurado en la misma trampa) — cae en el contenedor del diálogo.

---

## 4. Verificación final — salida real

### Frontend
```
$ npm run lint && npm test && npm run build
(lint sin salida — limpio)
Test Files  22 passed (22)
     Tests  126 passed (126)
(123 al cierre de V1 + 3 tests de regresión nuevos de M3: auto-foco, Escape, restauración de foco)
✓ built in <1s
```

### Backend (vía Docker — `pi_metis-backend-1`)
```
$ docker exec pi_metis-backend-1 ruff check metis/
All checks passed!

$ docker exec pi_metis-backend-1 ruff format --check metis/
64 files already formatted

$ docker exec pi_metis-backend-1 pytest -m unit -q
131 passed, 1 skipped
```
Re-verificado al cierre de la pasada (no solo al principio, en V2) — ningún archivo
`backend/metis/*.py` cambió entre medio, así que el resultado no podía haber cambiado, pero se
corrió igual en vez de asumirlo.

### Chequeo de códigos de error — las tres direcciones (F1/M2)
```
$ bash ./scripts/check-error-catalog.sh
OK — backend emite, ausente del catálogo
OK — catálogo, ausente del diccionario del frontend
OK — diccionario del frontend, ausente del catálogo

Catálogo de códigos de error sincronizado en las tres direcciones.
```

### Referencias e integridad
```
$ [sweep completo sobre todo *.md del repo, resolviendo cada enlace relativo]
(sin salida — cero enlaces rotos)

$ grep -rn "primera instancia de avance" .claude/ CLAUDE.md
architecture.md:3: ...(cita histórica dentro de la nota de "Última actualización" que
explica qué se corrigió — no una afirmación activa; el cuerpo de la sección ya no la
contiene)

$ git status
On branch fix/frontend-pasada2
nothing to commit, working tree clean
```

**CI en el PR — no verificable todavía.** No hay PR abierto (ver §2). El job nuevo
`error-catalog` se verificó localmente (`bash ./scripts/check-error-catalog.sh`, dos veces —
limpio y forzado a fallar con una inyección de prueba) pero no corrió dentro de GitHub Actions
todavía.

---

## 5. Qué queda pendiente

- **Mergear `fix/frontend-pasada2` a `staging`** — bloqueado por acceso a GitHub, ver §2.
- **DECISIÓN 043** (contraste WCAG) — pendiente de que Kevin/Octavio decidan aplicar la propuesta,
  ajustarla, o aceptar el contraste actual.
- Los pendientes que ya venían de la pasada 2 sin tocar en esta (DECISIÓN 036/037 — partición de
  Cramer, `etapas`/`AnalysisRequest`) siguen exactamente igual — explícitamente fuera de alcance
  de esta pasada también.

# Subir el frontend a GitHub — guía paso a paso

**Para:** Kevin, o un agente que lo asista.
**Fecha:** 29 de Julio de 2026.
**Este archivo no se commitea.** Es guía operativa, no documentación del proyecto. Borralo al
terminar (aparece como `?? INSTRUCCIONES-PR-frontend.md` en `git status` — es lo único sin
trackear ahora mismo, y así debe quedar).

---

## Dónde trabajar

**Carpeta:** `C:\Users\kevin\OneDrive\Desktop\PI_METIS` — la original, la que tiene la historia
completa.

**No usar** `C:\Users\kevin\OneDrive\Desktop\PR\PI_METIS`. Ese clon limpio tiene los archivos
pero no la historia: git lo ve como un único bulto de ~10.700 líneas sin saber que fueron seis
fases de frontend más tres pasadas de revisión. La carpeta original ya tiene todo lo necesario;
no hay nada que "pasar" a ningún lado. Cuando esto termine, el clon de `PR\` se puede borrar.

## Estado de partida (verificado)

```
Repositorio:      https://github.com/CarpinetiOctavio/PI_METIS
origin/staging →  3657ab0   Merge pull request #16 (feature/auth-refactor)
staging local  →  243f327   +30 commits  (Fase 0 y Fases 1-5 del frontend)
HEAD           →  4e51294   +33 commits  (pasadas 2 y 3 de mejora)
Rama actual:      fix/frontend-pasada2
Total sin subir:  63 commits
```

## Qué vamos a hacer

Subir esos 63 commits a GitHub en **dos pull requests hacia `staging`**:

| PR | Rama | Qué cuenta | Commits |
|---|---|---|---|
| **A** | `feature/frontend-fases0-5` | Construimos el frontend | 30 |
| **B** | `fix/frontend-pasada2` | Lo revisamos, documentamos y corregimos | 33 |

Dos y no uno porque son dos historias distintas, y un PR de 63 commits mezclándolas sería
ilegible para Octavio y para el tribunal.

**Nunca `git push origin staging`.** Los 30 commits del frontend se hicieron directo sobre
`staging` local, sin PR. GitHub tiene un Ruleset activo que bloquea el push directo y lo va a
rechazar — y si no lo rechazara sería peor, porque saltearía CI y la revisión de Octavio. La
rama `feature/frontend-fases0-5` del paso 3 existe justamente para no tener que tocar `staging`.

---

## Paso 1 — Backup fuera de OneDrive

Copiá la carpeta completa (incluida `.git`) a un ZIP en un disco externo o en `C:\backups\`.
Fuera de OneDrive: sincronizar un `.git` vivo puede corromperlo, y ya tuvimos un susto con esto.

Cinco minutos. Después de este paso, nada de lo que sigue puede perder trabajo.

## Paso 2 — Instalar y autenticar `gh`

Fue lo que bloqueó el merge en la pasada 3: no hay `gh` CLI ni token en esta máquina.

```bash
winget install --id GitHub.cli
```

Cerrá y reabrí la terminal, y después:

```bash
gh auth login       # elegí GitHub.com → HTTPS → autenticar por navegador
gh auth status      # tiene que decir "Logged in to github.com as ..."
```

**Alternativa sin `gh`:** los pushes funcionan igual, y los PRs se abren desde la web. Cada paso
de abajo tiene su variante.

## Paso 3 — Verificar el punto de partida

```bash
cd C:\Users\kevin\OneDrive\Desktop\PI_METIS
git fetch origin
git status --short
git log -1 --oneline
git rev-list --count origin/staging..HEAD
git rev-list --count origin/staging..staging
git rev-list --count staging..HEAD
```

Esperado:

| Comando | Resultado esperado |
|---|---|
| `git status --short` | solo `?? INSTRUCCIONES-PR-frontend.md` |
| `git log -1 --oneline` | `4e51294 docs: close pasada 3 with results report` |
| `origin/staging..HEAD` | `63` |
| `origin/staging..staging` | `30` |
| `staging..HEAD` | `33` |

**Si algún número no coincide, pará acá y reportá los reales.** No sigas asumiendo que este
documento tiene razón — puede estar desactualizado respecto de lo que haya pasado después.

## Paso 4 — Crear y subir la rama del PR A

```bash
git branch feature/frontend-fases0-5 staging
git push -u origin feature/frontend-fases0-5
```

Es el primer push de todo este trabajo. **Mirá la salida:** si menciona miles de líneas
cambiadas en archivos que nadie tocó, es `.gitattributes` renormalizando line endings — pará y
avisá antes de seguir.

## Paso 5 — Abrir el PR A como borrador

Borrador a propósito: **CI nunca corrió sobre ninguna línea de este trabajo.** Ni sobre las
~5.700 líneas del frontend, ni sobre el job `frontend`, ni sobre `error-catalog`. Conviene
descubrir los problemas antes de pedirle revisión a Octavio.

```bash
gh pr create --draft --base staging --head feature/frontend-fases0-5 \
  --title "feat(frontend): implementación del frontend, Fase 0 a Fase 5"
```

`gh` abre un editor para el cuerpo — pegá el texto del **Anexo A** de abajo.

**Sin `gh`:** entrá a https://github.com/CarpinetiOctavio/PI_METIS, GitHub va a ofrecer
"Compare & pull request" para la rama recién subida. Base `staging`, y tildá **Create as draft**.

## Paso 6 — Dejar correr CI y arreglar lo que aparezca

```bash
gh pr checks --watch
```

O la pestaña **Checks** del PR en la web. Tienen que pasar cuatro jobs: `lint`, `test`,
`error-catalog`, `frontend`.

Si algo falla:

| Síntoma | Qué hacer |
|---|---|
| `npm ci` falla | El lockfile está trackeado, es `lockfileVersion 3` y cubre todas las deps incluida `msw`, así que no debería. Si falla igual: `cd frontend && npm install`, commitear el lockfile actualizado |
| El job `frontend` falla en `npm run build` | `tsc -b` es más estricto que el dev server. Leer el error, suele ser un tipo faltante |
| `error-catalog` falla | Correr `bash ./scripts/check-error-catalog.sh` local: te dice exactamente qué código y en qué dirección |
| Diff enorme de line endings | **Parar. No mergear.** Es `.gitattributes`, avisá antes de seguir |

Arreglá con **commits nuevos** sobre la misma rama. No uses `--amend` ni `push --force` en una
rama que ya tiene PR abierto.

## Paso 7 — Sacar el borrador y mergear el PR A

Con los cuatro jobs verdes:

```bash
gh pr ready
gh pr edit --add-reviewer CarpinetiOctavio
```

Que lo mergee Octavio, o vos con su aprobación.

### ⚠️ Avisarle a Octavio: tiene que ser "Create a merge commit"

**No "Squash and merge" ni "Rebase and merge".** No es preferencia estética — las dos rompen el
paso 8.

Si el PR A se squashea, los 30 commits se colapsan en uno nuevo y `243f327` deja de ser parte de
la historia de `staging`. La rama `fix/frontend-pasada2` sí lo tiene como ancestro, así que git
pierde el punto de referencia común: el PR B mostraría **63 commits en vez de 33**, con las
~5.700 líneas del frontend reapareciendo como si fueran cambios de la pasada 2, y conflictos
casi garantizados. `Rebase and merge` tiene el mismo efecto sobre la ascendencia.

Con merge commit, el paso 8 son dos comandos y nada más.

Aparte de eso: los 30 commits por fase son el valor de este PR ante el tribunal. Squashearlos
tira la trazabilidad que casi perdimos una vez ya.

## Paso 8 — Abrir el PR B

Recién después de que A esté mergeado. **No hace falta cambiar de rama ni actualizar `staging`
local:** GitHub calcula el diff contra el `staging` del servidor por su cuenta, y la rama ya
desciende de los mismos commits que el PR A acaba de meter ahí.

```bash
cd C:\Users\kevin\OneDrive\Desktop\PI_METIS
git branch --show-current        # debe decir: fix/frontend-pasada2
git push -u origin fix/frontend-pasada2
gh pr create --draft --base staging --head fix/frontend-pasada2 \
  --title "docs+fix(frontend): reintegración documental y correcciones (pasadas 2 y 3)"
```

Cuerpo en el **Anexo B**. Después repetí los pasos 6 y 7 para este PR.

> **Por qué no hay `git checkout staging` ni `git rebase` acá.** Una versión anterior de esta
> guía los incluía "por prolijidad". Son innecesarios y `git checkout staging` es alarmante sin
> motivo: hace desaparecer de la carpeta todos los archivos de las pasadas 2 y 3
> (`decision043.md`, `scripts/`, `DECIMALS = 5`) hasta que volvés a la rama. No se pierde nada
> —viven dentro de los 33 commits— pero es un susto a cambio de nada. Y `rebase` era el único
> comando de toda esta guía que reescribía commits.

### Solo si GitHub avisa "This branch has conflicts"

Puede pasar si en el paso 6 hiciste commits de arreglo sobre `feature/frontend-fases0-5` que
tocaron los mismos archivos que las pasadas 2 o 3. En ese caso, y solo en ese caso:

```bash
git fetch origin
git merge origin/staging      # merge, NO rebase — no reescribe tus commits
```

Resolvé los conflictos que aparezcan y volvé a pushear. **Si no hay aviso de conflictos, no
corras nada de esto.**

## Paso 9 — Cierre

- **No mergear a `main`.** Los milestones ponen el primer merge a `main` en M5, y M1 todavía
  tiene dos criterios abiertos.
- Actualizar `.claude/rules/sprint.md`: hoy dice que los commits de Fases 1-5 están "mergeado a
  staging ✓". Era verdad localmente y falso en GitHub; recién ahora pasa a ser verdad de las dos.
- Borrar `INSTRUCCIONES-PR-frontend.md` y el clon de `Desktop\PR\PI_METIS`.

---

## Anexo A — Cuerpo del PR A

```markdown
## Qué trae

Implementación del frontend de CU-01/CU-02: Vite + React + TypeScript, tema "Instrumento",
8 pantallas, integración real contra el backend.

- **Fase 0** — scaffold, tokens del tema, routing, job de CI del frontend.
- **Fase 1** — auth end-to-end (login, registro, verificación, guards, logout).
- **Fase 2** — configuración + stream de Etapa 1 vía SSE-sobre-fetch, modal de atípico de Chow.
- **Fase 3** — resultados de Etapa 1 en los tres modos de presentación.
- **Fase 4** — historial: lista paginada y detalle.
- **Fase 5** — Etapa 2 mockeada con MSW y marca visual `PendingBadge`.

## Verificado contra el backend real (Docker, no mockeado)

Login/logout/me, configuración→stream con un CSV de 40 años y un atípico forzado, los tres modos
de resultados, e historial lista+detalle. Dos bugs reales de `useAnalysisStream` aparecieron
recién en esa verificación y están corregidos, cada uno con su test de regresión.

Único tramo sin verificar: registro→verify, bloqueado por falta de credenciales SMTP en
desarrollo.

## Qué NO trae

- Etapa 2 real — está mockeada con marca visual (ver DECISIÓN 042).
- Exportación a PDF.
- CU-03.

## Lectura recomendada para revisar

- `docs/frontend/informe-implementacion-frontend-fase1-6.md` — resumen navegable.
- `docs/frontend/frontend-implementation-plan.md` §10 — detalle decisión por decisión.

## Nota

Estos 30 commits se venían acumulando en `staging` local sin subir. Se publican como rama propia
para pasar por PR y CI, en vez de sincronizar `staging` a la fuerza.
```

## Anexo B — Cuerpo del PR B

```markdown
## Qué trae

Dos rondas de revisión sobre el trabajo del PR anterior, cada una ejecutada contra un plan
escrito (`docs/frontend/plan-mejora-frontend-pasada2.md` y `-pasada3.md`) con su informe de
resultados verificable.

### Reintegración documental

- **8 decisiones nuevas** (`DECISIÓN 036` a `043`) siguiendo la convención de `docs/decisiones/`.
  Incluye tres hallazgos de backend que estaban documentados solo en comentarios de código:
  partición de Cramer inalcanzable por el endpoint (036), `etapas` descartado y `AnalysisRequest`
  sin cablear (037), y catálogo de errores desincronizado (038).
- `CLAUDE.md`, `sprint.md`, `architecture.md`, `api-contracts.md` y `docs/README.md` puestos al
  día — varios afirmaban cosas que el código ya contradecía.
- Colisión de tres esquemas de numeración de decisiones resuelta
  (`DECISIÓN NNN` / `FE-NN` / `UX-A..D`).
- Un criterio de M1 cerrado: verificación E2E con CSV real contra el backend.

### Correcciones de código

Formateo numérico consistente (5 decimales, trazable a la precisión con la que la tesis de
Facundo reporta sus valores), `abort()` del stream al desmontar, mensajes de error del
diccionario curado en vez de errores crudos de JS, spinner de carga en los guards, y cierre de
Fase 6 (accesibilidad del modal de atípico: `inert`, auto-foco, Escape que no decide,
restauración de foco).

### Infraestructura

- `.gitattributes` — normalización de line endings, el primero del repo.
- `scripts/check-error-catalog.sh` + job `error-catalog` en CI: hace cumplir automáticamente la
  regla de `DECISIÓN 038`. Verificado en los dos sentidos — corre limpio contra el repo, y falla
  con exit 1 ante una inyección de prueba.

## Pendiente de decisión

`DECISIÓN 043` — propuesta de contraste WCAG AA para el tema Instrumento. Hallazgos y propuesta
calculada cerrados; los tokens no se tocaron porque es identidad visual fijada.
```

---

## Lo que no hay que hacer

- **No `git push origin staging`** — el Ruleset lo rechaza, y si no lo hiciera saltearía CI.
- **No desactivar el Ruleset** "solo por esta vez".
- **No mergear a `main`** — primer merge a `main` = M5.
- **No `push --force`** en una rama con PR abierto.
- **No `git rebase`** en ningún momento de este procedimiento — no hace falta. Si hay conflictos,
  `git merge origin/staging` (ver paso 8).
- **No squashear** el PR A — los 30 commits por fase son el valor.
- **No trabajar desde el clon de `Desktop\PR\`** — no tiene la historia.
- **No commitear este archivo.**

## Chequeo final

```bash
git status                                    # limpio (o solo este archivo, si todavía no lo borraste)
git rev-list --count origin/staging..HEAD     # 0 después de mergear los dos PRs
bash ./scripts/check-error-catalog.sh         # las tres direcciones OK
cd frontend && npm run lint && npm test && npm run build
docker-compose up -d backend postgres
docker ps                                     # confirmar el nombre real del contenedor
docker exec <backend> pytest -m unit -v        # esperado: 131 passed, 1 skipped
```

En GitHub: los cuatro jobs verdes en cada PR, y `origin/staging` conteniendo los 63 commits.

## Nota para el agente que ejecute esto

Reportá los números **reales** de cada comando, no los esperados. En las tres pasadas anteriores
el conteo de commits se reportó mal dos veces por estimarlo en vez de correr
`git rev-list --count`. Si un número no coincide con lo que dice este documento, pará y reportá
en vez de continuar.

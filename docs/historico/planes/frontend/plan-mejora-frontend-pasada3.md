# Plan de Mejora — Pasada 3 sobre el Frontend (cierre)

**Fecha:** 29 de Julio de 2026.
**Origen:** revisión independiente de
[`informe-pasada2-resultados.md`](./informe-pasada2-resultados.md), verificada contra el repo
real (no solo leída).
**Destinatario:** la próxima sesión de Claude Code.
**Alcance:** cerrar los gaps que quedaron de la pasada 2, mergear a `staging`, y terminar
Fase 6 del frontend.

---

## 0. Contexto — esta pasada es chica

La pasada 2 fue sólida. Se verificó independientemente y se confirma: 035 correctamente
reservado y 036-042 creados e indexados; **cero enlaces markdown rotos sobre 99 documentos**
(el riesgo real de haber movido cuatro archivos a `docs/frontend/`); cero referencias al
esquema viejo `Decisión D` en código; `.gitattributes` funcionando; y D1, D2, D4, D5, D6, D7,
D8, D10 implementados tal como se describen.

Dos aciertos que conviene no romper: **`inert` está resuelto correctamente** (seteado
imperativamente sobre el nodo DOM vía ref, no como prop JSX — React 18 no soporta la prop y
pasarla habría sido un no-op silencioso), y `format.ts` justifica su criterio contra
`testing.md` en vez de elegirlo al azar.

**Corrección de la pasada anterior, para el registro:** el plan de la pasada 2 afirmaba que
`.claude/launch.json` era "probablemente inerte, convención de VS Code". Era falso. Es la
configuración real que lee `preview_start` de Claude Code para levantar el dev server, con
exactamente los campos que tiene el archivo, y está pensada para commitearse. La pasada 2 hizo
bien en corregir la premisa en vez de obedecerla. Ese es el comportamiento esperado: **si un
plan afirma algo que el código o la documentación oficial contradicen, se verifica y se corrige
el plan, no se ejecuta la instrucción equivocada.**

### Reglas de alcance

**SÍ entra:** verificación de la pasada 2, los cinco fixes del Bloque F, las tres mejoras del
Bloque M, el merge a `staging`, y el cierre de Fase 6 del frontend.

**NO entra:**
- Implementar DECISIÓN 036 o 037 (partición de Cramer, `etapas`/`AnalysisRequest`). Es trabajo
  de backend para M2, no de esta serie.
- Modificar `backend/metis/core/`.
- Aplicar la propuesta de contraste de D11 a `tokens.instrumento.css`. Es identidad visual
  fijada; en esta pasada solo se **reubica** la propuesta, no se ejecuta.
- Renumerar decisiones existentes.

---

## Bloque V — Verificación (primero, antes de tocar nada)

La revisión externa **no pudo reproducir** las salidas verdes del informe de la pasada 2: el
`node_modules` del repo está instalado para Windows (falta `@rollup/rollup-linux-x64-gnu` al
leerlo desde otro sistema) y el lint se pasó de timeout. Sí se verificó estáticamente que el
conteo de tests cierra: 93 `it(` — eran 89, +4 de D2/D5/D7/D8 — más dos `it.each`
parametrizados sobre los tokens ≈ 123, coherente con lo reportado.

Pero **coherente no es verificado.**

### V1 — Reproducir el verde del frontend

```bash
cd frontend && npm run lint && npm test && npm run build
```

Pegar la salida real en el informe. Si algo sale rojo, **arreglarlo antes de seguir con
cualquier otro bloque** — significa que la pasada 2 cerró sobre una afirmación falsa y eso
cambia el orden de prioridades de todo este plan.

### V2 — Correr `pytest` de backend por primera vez

La pasada 2 no pudo (el Python de la máquina no tiene las dependencias del proyecto, no hay
`venv` en el repo). El argumento de alcance era válido — no se tocó ni un `.py` de
`backend/metis/` — pero M1 tiene un criterio de testing abierto y el repo verifica el backend
vía Docker, no vía el Python del host (`sprint.md`).

```bash
docker-compose up -d backend postgres
docker exec <backend> ruff check metis/
docker exec <backend> ruff format --check metis/
docker exec <backend> pytest -m unit -v
```

Verificar el nombre real del contenedor con `docker ps` antes — el prefijo lo decide Docker
Compose a partir del nombre del directorio y ya cambió una vez en este repo (`pi-postgres-1`
vs. `pi_metis-postgres-1`, ver `sprint.md`).

**Si sale verde:** documentar en `sprint.md` que la suite de backend corre reproduciblemente
vía Docker, y **agregar el procedimiento a `CLAUDE.md`** en la sección de comandos — hoy
`CLAUDE.md` dice `cd backend && pytest -v` como si el host tuviera las dependencias, y no las
tiene. Es una trampa documentada para la próxima sesión.

---

## Bloque F — Gaps encontrados en la revisión

### F1 — Dos códigos del frontend no viven en ningún catálogo

El chequeo bidireccional de la pasada 2 usó un regex demasiado ruidoso (devolvía `A`, `E`, `P`
como si fueran códigos) y eso tapó un gap real. Con un regex limpio:

- **Backend → catálogo: cero gaps.** A3 está genuinamente cerrado en esa dirección.
- **Catálogo → `errors.es.ts`:** solo `DIST_*` (Etapa 2, esperado y documentado).
- **`errors.es.ts` → catálogo: `STREAM_CONNECTION_ERROR` y `VALIDATION_ERROR` no existen en
  ningún contrato.** Son códigos que el frontend inventa y le muestra al usuario.

DECISIÓN 038 estableció el catálogo de `api-contracts.md` como fuente única, pero la regla
quedó escrita en una sola dirección (`core/`/`services/` → catálogo). Los códigos originados
en el frontend no tienen casa.

**Tarea.** Resolver explícitamente, y dejar el criterio en un **addendum fechado dentro de
`decision038.md`** (no en una decisión nueva — es la misma decisión con información más
reciente, ver `docs/decisiones/README.md`, "Addendums"). Opciones:

1. Subsección nueva en `api-contracts.md` — "Códigos originados en el frontend" — con ambos.
2. Declarar la regla explícitamente unidireccional y documentar dónde viven los códigos del
   frontend (`errors.es.ts` como su propia fuente).

Recomendación: opción 1. El catálogo se llama "fuente única"; que dos códigos visibles al
usuario vivan fuera de él contradice el nombre.

**Reemplazar además el regex de verificación** que `decision038.md` documenta como
reproducible, por uno que no genere ruido. Este funciona en las dos direcciones:

```bash
# Emitidos por el backend y ausentes del catálogo
grep -rhoE '"(AUTH|CONTRACT|TEST|DIST|PARSE|SESSION)_[A-Z_]+"' backend/metis/ \
  | tr -d '"' | sort -u > /tmp/emit.txt
grep -ohE '\b(AUTH|CONTRACT|TEST|DIST|PARSE|SESSION)_[A-Z_]+' \
  .claude/rules/architecture/api-contracts.md | sort -u > /tmp/cat.txt
comm -23 /tmp/emit.txt /tmp/cat.txt

# Del catálogo y ausentes del diccionario del frontend
grep -ohE '^  [A-Z_]+:' frontend/src/i18n/errors.es.ts | tr -d ' :' | sort -u > /tmp/fe.txt
comm -23 /tmp/cat.txt /tmp/fe.txt

# Del frontend y ausentes del catálogo  ← la dirección que faltaba
comm -13 /tmp/cat.txt /tmp/fe.txt
```

**Criterio de hecho:** las tres direcciones devuelven solo lo esperado y documentado
(`DIST_*` mientras Etapa 2 no esté expuesta), y el addendum de 038 explica por qué cada
excepción es aceptable.

### F2 — La afirmación de D3 es inexacta

El informe de la pasada 2 dice *"aplicado a todo `className='num'`"*. No lo está:

- `frontend/src/routes/design-events/DesignEventsPage.tsx` — el número grande del evento de
  diseño tiene `className="num"` sin `formatNum`.
- `frontend/src/routes/ranking/RankingPage.tsx` — renderiza `EEA {item.eea}` crudo.

Son pantallas mock hoy, pero se vuelven reales en M2 y el formateo se va a olvidar.

**Tarea.** Aplicar `formatNum` en ambas. Si el valor mock no tiene la precisión de un dato
real, no importa — lo que se está fijando es el patrón, no el número.

### F3 — `architecture.md` sigue afirmando algo falso, y es lectura obligatoria

`.claude/rules/architecture/architecture.md`, sección "Nginx como reverse proxy":

> *"El frontend entra en operación recién en la primera instancia de avance del proyecto
> (mediados de agosto de 2026) — hasta entonces, nginx no tiene build estático que servir."*

`CLAUDE.md` señala correctamente que está desactualizado, pero decidió no corregirlo por no
ser archivo de arquitectura. El problema: `architecture.md` está en la lista **"leer siempre al
comienzo de cualquier sesión"** de `CLAUDE.md`. Dejar ahí una afirmación que sabemos falsa, con
la corrección en otro archivo, es exactamente el patrón que la pasada 2 vino a eliminar.

**Tarea.** Corregir la frase en `architecture.md` (el frontend ya está integrado contra el
backend real; lo que sigue sin existir es el build servido por nginx, que es otra cosa).
Actualizar la línea de "Última actualización" del encabezado del archivo, que es la convención
que ese documento ya usa. Sacar de `CLAUDE.md` la nota de "señalarlo si se toca ese documento",
que queda sin objeto.

### F4 — Formateo numérico a 5 decimales

`format.ts` usa 4 decimales, justificados contra la tolerancia `abs=1e-4` de los tests de
regresión de `testing.md`. Es un argumento válido, pero la tesis de Facundo imprime **5**
decimales en los valores que este proyecto usa como referencia de verificación
(`tau_w1=0.18289`, `tau_w2=0.35206`, `t_w1=1.13970`, `t_w2=1.08774` — ver
`formulas-etapa1.md` §6).

**Decisión de Kevin: subir a 5 decimales fijos.** Trazabilidad directa a la fuente
bibliográfica primaria, que es el criterio que rige el resto del proyecto.

**Tarea.** `DECIMALS = 5` en `frontend/src/i18n/format.ts`. Actualizar el docstring: el
criterio ya no es la tolerancia de los tests sino **la precisión con la que la tesis reporta
sus propios resultados**, que es contra lo que un docente va a comparar la pantalla. Citar
`formulas-etapa1.md` §6 con los valores concretos. Ajustar los tests que asserten sobre 4
decimales.

Queda registrado como limitación aceptada (no hace falta resolverla acá): con decimales fijos,
un valor mucho menor que `1e-5` — por ejemplo un `r_k` de Anderson muy chico — se muestra como
`0,00000`. Si al ver las tablas reales el relleno de ceros molesta visualmente,
`minimumFractionDigits: 0` lo elimina sin tocar el tope de 5; es un cambio de un carácter.

### F5 — Menores

- El informe de la pasada 2 dice **"18 commits"**; son **22** (`git rev-list --count
  staging..HEAD`). Corregir el encabezado del informe.
- `frontend/src/routes/config/ConfigPage.tsx` cita `metis-wireframes-fase1-decisiones.md` sin
  ruta. Ahora que `frontend-design/` está trackeado, la ruta es resoluble: usar
  `frontend/frontend-design/metis-wireframes-fase1-decisiones.md`.

---

## Bloque M — Mejoras

### M1 — La propuesta de contraste de D11 está en el lugar equivocado

La auditoría WCAG de D11 produjo una propuesta concreta y calculada (tabla de tokens con
valores nuevos y ratios resultantes), y quedó registrada en `.claude/rules/sprint.md`.

`sprint.md` es un documento de sprint — se reescribe, se tacha, se reorganiza. Una propuesta
calculada sobre la identidad visual del producto se va a perder ahí. Además cumple el criterio
de promoción que la propia DECISIÓN 039 estableció: **restringe decisiones futuras.**

**Tarea.** Crear `docs/decisiones/decision043.md` — "Contraste WCAG AA del tema Instrumento:
hallazgos y propuesta, no aplicada". Contenido: metodología (fórmula de luminancia real, 21
pares, fondos `color-mix()` compuestos y no el color sólido), los dos hallazgos, la tabla de
propuesta, y el estado explícito **PENDIENTE DE DECISIÓN — Kevin/Octavio**. Reservar 043 en el
índice de `docs/decisiones/README.md` antes de escribir. Reemplazar el bloque de `sprint.md`
por una referencia de una línea a la decisión.

### M2 — Hacer cumplible la regla de DECISIÓN 038

*"Todo código nuevo emitido por `core/` o `services/` se agrega al catálogo en el mismo commit
que lo introduce"* es hoy una regla que depende de que alguien se acuerde. El chequeo
bidireccional de F1 son cuatro líneas de shell.

**Tarea.** Agregar un job (o un step dentro del job `lint`) a `.github/workflows/ci.yml` que
corra el chequeo y falle si aparece un código sin catalogar. Las excepciones conocidas
(`DIST_*` mientras Etapa 2 no esté expuesta) van como allowlist explícita **en un archivo
versionado, con comentario de por qué cada una está ahí** — no hardcodeadas en el YAML sin
explicación. Documentar el job como addendum en `decision038.md`, junto con F1.

### M3 — Cerrar Fase 6 del frontend

Quedó más barata de lo que parece. Con `inert` ya aplicado al contenedor de fondo, el foco no
puede escaparse del diálogo — el grueso del focus trap está resuelto de hecho. Falta:

1. **Auto-foco al abrir** el modal de atípico — al primer elemento interactivo, o al contenedor
   del diálogo con `tabIndex={-1}`.
2. **Cierre con Escape.** Ojo con la semántica: cerrar el modal **no** puede significar
   descartar la decisión. El backend está bloqueado esperando (`session_store`, 300s) y el
   pipeline no continúa sin respuesta. Escape debe devolver el foco y dejar el modal abierto, o
   equivaler explícitamente a una de las dos decisiones. **Es una decisión de producto, no de
   accesibilidad** — resolverla explícitamente y dejar constancia; no elegir la que sea más
   fácil de implementar.
3. **Restaurar el foco** al elemento que lo tenía cuando el modal se cierra.

Test de regresión para cada una. Con esto Fase 6 pasa de "parcial" a completa salvo D11, que
queda como decisión abierta de identidad visual (M1).

---

## Bloque G — Merge a `staging`

**Decisión de Kevin: mergear antes de arrancar la pasada 3.** La rama sale de `staging` limpio,
el historial queda legible, y CI valida un bloque cerrado a la vez en vez de un PR gigante que
mezcla dos rondas.

### G1 — PR de `fix/frontend-pasada2` → `staging`

**Antes de abrir el PR:** V1 y V2 en verde. No se abre un PR sobre afirmaciones sin verificar.

- 22 commits. `constraints.md`: nunca merge directo a `main`; `staging` no admite commits
  directos.
- CI debe pasar los tres jobs (`lint`, `test`, `frontend`).
- **Atención con `.gitattributes`:** es el primero del repo. Si al mergear aparece una
  renormalización masiva de line endings, **parar y avisar** — no commitear 38.000 líneas de
  cambio de CRLF mezcladas con el resto. En el checkout verificado no aparece (el árbol da
  limpio), pero es el momento exacto donde ese tipo de cosa se manifiesta.

### G2 — Rama de la pasada 3

Sale de `staging` **ya con la pasada 2 mergeada**. Nombre sugerido: `fix/frontend-pasada3`,
manteniendo la serie. Si el contenido termina siendo mayoritariamente documentación otra vez,
vale renombrarla antes del PR — pero no partir la serie a mitad de camino.

---

## Orden de ejecución

```
1. V1 → V2                       ← si algo sale rojo, se replantea todo lo demás
2. G1  (merge de pasada 2)       ← sobre verde verificado, no antes
3. F1 → F2 → F3 → F4 → F5        ← gaps
4. M1 → M2                       ← reubicar D11, CI del catálogo
5. M3                            ← cierre de Fase 6
6. Verificación final
```

## Verificación final

Con salida real pegada en el informe, no afirmada:

1. `npm run lint && npm test && npm run build` — verde, con el conteo de tests (debería subir
   respecto de 123 por los tests de M3).
2. `pytest -m unit -v` vía Docker — verde.
3. **Las tres direcciones** del chequeo de códigos de F1, no dos.
4. Sweep de enlaces relativos sobre todo `*.md` — cero rotos. Se rompen justo cuando se agregan
   decisiones nuevas y se mueven bloques entre archivos, que es lo que hace M1.
5. `git status` limpio y CI verde en el PR.
6. `grep -rn "primera instancia de avance" .claude/ CLAUDE.md` → cero (F3).

## Formato del informe de resultados

Mismo formato que `informe-pasada2-resultados.md`, que estuvo bien: una fila por ítem
(V1-V2, F1-F5, M1-M3, G1-G2) con estado hecho / parcial / no hecho / descartado con motivo.
Ninguno omitido.

Agregar además:

- **Toda premisa de este plan que resulte incorrecta**, con la evidencia que lo demuestra —
  igual que la pasada 2 hizo con `.claude/launch.json`. Un plan corregido es un resultado
  válido; una instrucción equivocada ejecutada al pie de la letra, no.
- El número de decisión finalmente asignado a M1 si difiere de 043.
- Cómo se resolvió la semántica de Escape en el modal (M3.2) y por qué.

# Fix — SonarCloud en el PR #18

**Fecha:** 29 de Julio de 2026. **Rama:** `fix/frontend-pasada2`.
**Contexto:** el PR #18 volvió a fallar el quality gate con ~100 issues. **~85 son ruido de una
sola causa** (abajo). Los reales son 9 y están en código nuestro.

---

## Paso 0 — Kevin, en la UI de SonarCloud (2 minutos, hacer primero)

**~85 de los ~100 issues están en `frontend/frontend-design/`** — prototipos HTML de diseño,
incluida la carpeta `versiones/`. No es código de producción.

`sonar-project.properties` **ya los excluye correctamente**, pero SonarCloud en modo *Automatic
Analysis* **ignora ese archivo** — es una limitación documentada. Las exclusiones tienen que
cargarse en la web.

SonarCloud → proyecto `CarpinetiOctavio_PI_METIS` → **Administration → Analysis Scope → Source
File Exclusions**:

```
frontend/frontend-design/**
frontend/public/mockServiceWorker.js
frontend/dist/**
```

Sin esto, arreglar lo de abajo no alcanza para que el gate pase.

> **Nota:** el `sonar-project.properties` commiteado no es inútil — pasa a estar activo el día
> que se migre a análisis por CI. Ver el Paso 3.

---

## Paso 1 — Los 9 issues reales

### 1.1 `scripts/check-error-catalog.sh` — **prioridad alta**

Los dos primeros son **Reliability High** y son, con toda probabilidad, lo que hoy tira el rating
de Reliability por debajo de A.

**L51 y L67 — usar `[[` en vez de `[`:**

```bash
# L51
if [[ -n "$diff" ]]; then
# L67
if [[ "$FAILED" -ne 0 ]]; then
```

**L52, L69-L72 — mensajes de error a stderr.** Un mensaje de fallo no va a stdout:

```bash
# L52, dentro de check_direction()
echo "FAIL — $label:" >&2
echo "$diff" | sed 's/^/  /' >&2

# L69-L72, dentro del bloque if [[ "$FAILED" -ne 0 ]]
echo >&2
echo "Hay códigos de error sin catalogar en alguna dirección. Agregarlos a" >&2
echo ".claude/rules/architecture/api-contracts.md y/o frontend/src/i18n/errors.es.ts," >&2
echo "o a scripts/error-catalog-allowlist.txt con un comentario que justifique" >&2
echo "por qué la excepción es legítima (ver DECISIÓN 038)." >&2
```

Los `echo "OK — $label"` y el mensaje final de éxito **se quedan en stdout** — no son errores.

**Verificar después:** el script tiene que seguir dando exit 0 en verde y exit 1 con una
inyección de prueba, igual que se validó en la pasada anterior.

```bash
bash ./scripts/check-error-catalog.sh; echo "exit=$?"
```

### 1.2 `frontend/src/api/sse.ts` L159 — bloques de `case` duplicados

Consecuencia directa del arreglo D1 de la pasada anterior: al hacer que `case "error"` use
`errorText()` igual que `case "contract_error"`, los dos bloques quedaron idénticos. Sonar tiene
razón y el arreglo mejora el código.

Fusionar los dos casos:

```ts
case "contract_error":
case "error":
  // (conservar el comentario que explica el criterio de DECISIÓN 038 / D1 —
  //  es la justificación de por qué ambos usan errorText y no event.mensaje)
  return {
    ...base,
    fase: "error",
    error: { codigo: event.codigo, mensaje: errorText(event.codigo) },
  };
```

**Cuidado con TypeScript:** los dos eventos son variantes distintas de la unión `SseEvent`. Al
unificar los `case`, el tipo de `event` dentro del bloque pasa a ser la unión de ambos —
verificar que `event.codigo` siga siendo accesible en las dos (lo es si ambas variantes lo
declaran). Si `tsc -b` protesta, no forzar con `as`: dejar los dos casos separados y marcar el
issue como *Won't fix* con ese motivo.

`sse.test.ts` cubre las dos rutas; tiene que seguir en verde sin tocarlo.

### 1.3 `frontend/src/mocks/PendingBadge.tsx` L16 — espaciado ambiguo

```tsx
<span className="visually-hidden"> — {text}</span>
```

El espacio inicial dentro del `<span>` es ambiguo para el parser de JSX. Explicitarlo:

```tsx
<span className="visually-hidden">{` — ${text}`}</span>
```

No cambiar el contenido: ese texto es el nombre accesible del badge (arreglo D10).

### 1.4 `frontend/src/routes/stream/StreamPage.tsx` L295 — listener en elemento no interactivo

El `onKeyDown` del Escape está sobre el `<div className="card" role="dialog">`. Sonar considera
`div` no interactivo aunque tenga `role`.

**No cambiar el comportamiento** — la semántica de Escape es una decisión de producto (M3.2,
DECISIÓN 044): no cierra el modal ni resuelve ninguna decisión. Opciones, en orden de preferencia:

1. Mover el listener a nivel documento con un `useEffect` activo solo mientras `modalOpen`, y
   sacarlo del `div`. Resuelve el issue y es más robusto: hoy, si el foco se escapa al `body`
   (por ejemplo un click en el backdrop), Escape no se captura.
2. Si la opción 1 rompe alguno de los tres tests de regresión de M3, dejarlo como está y marcar
   el issue como *Won't fix* citando la decisión.

Correr `StreamPage.test.tsx` completo después.

### 1.5 `frontend/src/routes/stream/StreamPage.tsx` L61 — comentario TODO

Severidad **Info**, 0 min de esfuerzo, **no afecta ningún rating**. Está dentro del bloque de
comentario que documenta D9 (por qué `summarizeGroup` no usa `nivel_independencia`).

Si el TODO ya no describe trabajo pendiente real, reescribir esa línea sin la palabra "TODO". Si
sí describe algo pendiente, dejarlo y marcar el issue como *Won't fix* — un TODO legítimo es
información, no deuda.

---

## Paso 2 — Verificar y subir

```bash
cd frontend && npm run lint && npm test && npm run build   # 126 tests
cd .. && bash ./scripts/check-error-catalog.sh             # exit 0
git push
```

El push re-dispara el análisis de SonarCloud automáticamente.

**Puede hacer falta más de una vuelta.** Cada re-análisis puede destapar algo nuevo en código que
Sonar acaba de ver por primera vez. Es normal, no es señal de que algo esté mal.

---

## Paso 3 — Addendum en `docs/decisiones/decision044.md`

Addendum fechado dentro del archivo existente, **no una decisión nueva** (ver
`docs/decisiones/README.md`, sección "Addendums"). Tres cosas:

1. **`sonar-project.properties` es inerte bajo Automatic Analysis.** SonarCloud ignora el archivo
   si el análisis es automático; las exclusiones viven en la UI. El archivo se conserva porque
   pasa a estar activo con el análisis por CI. Dejar constancia de que ambos lugares tienen que
   mantenerse en paridad mientras convivan.
2. **Los issues marcados *Won't fix* en esta ronda**, si los hubo (1.2, 1.4 o 1.5), con su motivo
   escrito. Mismo criterio que el rechazo del `<dialog>` nativo.
3. **La migración a análisis por CI queda agendada.** Es una sola migración que resuelve las dos
   cosas de Sonar que siguen abiertas: hace válidas las exclusiones del archivo **y** habilita
   importar cobertura (hoy 126 tests de frontend y 131 de backend sin ningún crédito). Requiere un
   `SONAR_TOKEN` como secret del repositorio — decisión de Kevin y Octavio, no de una sesión de
   agente.

---

## Notas para el agente

- **El Paso 0 lo hace Kevin en la web.** Si no está hecho, los ~85 issues de `frontend-design/`
  siguen ahí y el gate no pasa por más que se arregle todo lo demás. Confirmar antes de dar la
  vuelta por cerrada.
- **1.2, 1.4 y 1.5 pueden terminar en *Won't fix*** si el arreglo choca con TypeScript, con los
  tests de M3, o con un TODO legítimo. Un issue rechazado con motivo escrito es un resultado
  válido; uno silenciado sin explicación, no. Precedente: el `<dialog>` nativo.
- Reportar números reales de cada comando, no los esperados.

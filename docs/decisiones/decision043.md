# DECISIÓN 043 — Contraste WCAG AA del tema Instrumento

**Fecha:** 29 de Julio de 2026 (auditoría, pasada 2) — promovida a `docs/decisiones/` el 29 de Julio de 2026 (M1, pasada 3) — **aplicada** el 18 de Agosto de 2026 (Bloque H2 del [plan post-avance](../plan-post-avance.md), decisión de Kevin).
**Estado:** Aplicada. Los cinco tokens de la tabla original se aplicaron, más un hallazgo nuevo (`.pill.acc`, ver más abajo). Verificado con test programático — ver "Criterio de hecho".

### Contexto
D11 (pendiente heredado de Fase 6 del frontend — pulido y accesibilidad) auditó el
contraste WCAG de `tokens.instrumento.css` en la pasada 2 de mejora. El resultado
(metodología, hallazgos, tabla de propuesta calculada) quedó registrado en
`.claude/rules/sprint.md` — un documento de sprint que se reescribe, se tacha y se
reorganiza con el tiempo. Una propuesta calculada sobre la identidad visual del
producto no debía vivir ahí: cumple el criterio de promoción que la propia
[DECISIÓN 039](decision039.md) estableció (**restringe decisiones futuras** — cualquier
cambio futuro a estos tokens tiene que resolver, o conscientemente ignorar, lo que
esta auditoría encontró). Movida acá en la pasada 3 (M1), sin cambiar una coma del
contenido técnico.

### Metodología
Contraste WCAG real — fórmula de luminancia relativa, no estimado a ojo — calculado
programáticamente sobre los 21 pares texto/fondo de `tokens.instrumento.css`,
incluidos los fondos compuestos reales de `color-mix(in srgb, ...)` que usan las
banners/pills de `ok`/`warn`/`crit` (no el color sólido de fondo — el primer intento
contra el fondo sólido daba falsos negativos, porque esas banners nunca se ven sobre
un fondo sólido en la UI real).

### Hallazgos reales (no falsos positivos)
1. **`--fnt`** (clase `.fn`, 11px — usado en decenas de lugares: notas al pie,
   `(n1=X, n2=Y)`, EEA de ranking, separadores) — **2.31:1 en modo claro,
   2.89-3.15:1 en modo oscuro**, muy por debajo del mínimo de 4.5:1 para texto
   normal. Es el hallazgo más extendido — `.fn` se usa en casi todas las pantallas.
2. **`--ok`/`--warn`/`--crit`** como texto sobre su propio fondo `color-mix`
   translúcido (banners/pills de warning) — **solo en modo claro**: ratios entre
   2.79:1 y 4.10:1 según el token y el % de mezcla (peor caso: `--warn` sobre
   `--bg`, 2.79-2.92:1 — ni siquiera cumple el umbral de 3:1 para texto grande/UI).
   Verificado que el modo oscuro no tiene este problema (5.16-8.59:1, todos aprueban).

### Propuesta original (pasada 2) — los cinco tonos se aplicaron tal cual; el rótulo "sobre `--bg`" de la última columna resultó impreciso, ver "Recalculado sobre los tokens actuales" más abajo

Mismo tono, oscurecido/aclarado lo mínimo necesario para llegar a 4.5:1.

| Token | Valor actual | Propuesta | Ratio resultante |
|---|---|---|---|
| `--fnt` (claro) | `#9aa5b1` | `#697888` | 4.51:1 vs. `--surf` |
| `--fnt` (oscuro) | `#566270` | `#728193` | 4.51:1 vs. `--surf` |
| `--warn` (claro) | `#b5791a` | `#825713` | 4.50:1 (peor caso, 18% sobre `--bg`) |
| `--ok` (claro) | `#128a4e` | `#0e6d3e` | 4.54:1 (peor caso, 18% sobre `--bg`) |
| `--crit` (claro) | `#c24444` | `#a83737` | 4.50:1 (peor caso, 18% sobre `--bg`) |

Estos valores **oscurecen/aclaran el mismo matiz** (no cambian de color) lo mínimo
necesario para cruzar 4.5:1 — son un piso computado, no una propuesta de diseño
terminada. `--acc`/`--acc2`/`--ink`/`--mut` ya cumplen AA en ambos modos, sin
cambios propuestos. `--line`/`--line-strong` no cumplen 3:1 contra `--bg`, pero son
separadores decorativos, no el único indicador de un borde interactivo — no se
proponen cambios ahí.

### Decisión

**Aplicar la propuesta** (Kevin, 18/08/2026, Bloque H2 del plan post-avance).
El tema Instrumento sigue siendo identidad visual fijada — esto no reabre
matices ni layout, solo la luminosidad de cinco tokens ya identificados.

### Recalculado sobre los tokens actuales antes de aplicar — no se copió la tabla a ciegas

El plan post-avance advertía explícitamente: la tabla de arriba se calculó
en la pasada 2, sobre un set de tokens anterior a `--glow`/`--acc2`
(pasada 5) y al `.pill.acc` del historial interactivo (Bloque C3). Antes de
tocar ningún hex se recalculó todo con una implementación propia de la
fórmula WCAG (`theme/contrast.ts`) sobre `instrumentoTokens` actual —
dos cosas salieron de esa verificación:

1. **La etiqueta "sobre `--bg`" de la tabla original era imprecisa.**
   Recalculando contra `--bg` los números no reproducían ni los hallazgos
   originales (2.79-4.10:1) ni el 4.50:1 prometido por la propuesta —
   salían sistemáticamente más bajos (ratios de FALLA incluso con los
   valores ya corregidos). `.pill`/`.step .node`/`.banner` viven siempre
   dentro de `.card` (`global.css`: `.card { background: var(--surf) }`),
   nunca directo sobre `--bg` — recalculando contra `--surf` (el fondo real
   donde aparecen) los números sí reproducen los de la auditoría original y
   la propuesta sí alcanza ~4.85-4.90:1 en el peor caso. Sin este paso se
   habría aplicado una propuesta ya verificada como insuficiente contra el
   fondo real, con el test en verde por estar midiendo el par equivocado.
2. **`.pill.acc` es un par nuevo que no estaba en las 21 combinaciones
   originales** — se agregó recién en el Bloque C3 (historial interactivo,
   DECISIÓN 062, 18/08/2026), después de la auditoría de la pasada 2. Texto
   `--acc` sobre su propio fondo mezclado al 16% (el valor con el que se
   implementó): **4.29:1 en modo claro, por debajo de 4.5:1.** `--acc` no
   se tocó (es el color de foco/selección en toda la app — cambiar el tono
   tenía mucho más radio de impacto que un solo pill); en cambio se bajó el
   `%` de mezcla del CSS de `.pill.acc` de 16% a 12% (`components.css`),
   que alcanza 4.53:1 sin cambiar ningún color.

### Aplicado

| Token | Valor anterior | Valor aplicado | Ratio verificado |
|---|---|---|---|
| `--fnt` (claro) | `#9aa5b1` | `#697888` | 4.52:1 vs. `--surf` |
| `--fnt` (oscuro) | `#566270` | `#728193` | 4.52:1 vs. `--surf` |
| `--warn` (claro) | `#b5791a` | `#825713` | 4.87:1 (peor caso, 18% sobre `--surf`) |
| `--ok` (claro) | `#128a4e` | `#0e6d3e` | 4.90:1 (peor caso, 18% sobre `--surf`) |
| `--crit` (claro) | `#c24444` | `#a83737` | 4.84:1 (peor caso, 18% sobre `--surf`) |
| `.pill.acc` mezcla | 16% | 12% | 4.53:1 (`--acc`, sin cambios, sobre `--surf`) |

`tokens.instrumento.css` y `tokens.ts` (`instrumentoTokens`) se actualizaron
juntos — `tokenParity.test.ts` los mantiene sincronizados. `--acc`/`--acc2`/
`--ink`/`--mut`/`--glow` sin cambios. `--line`/`--line-strong` sin cambios
(separadores decorativos, nunca el único indicador de un borde
interactivo). Los fondos animados (`--glow`/`--acc2` leídos en cada frame,
`readCssVar` dentro de `draw`) no se ven afectados — ninguno de los tokens
tocados es de acento; verificado en el navegador de dev con los fondos
encendidos, sin errores de consola tras el cambio de tema claro/oscuro.

### Criterio de hecho
- `theme/contrast.test.ts` — 10 tests (`fnt`/`surf` + el peor caso de
  `ok`/`warn`/`crit`/`acc` sobre su propio fondo compuesto, en los dos
  modos), todos ≥4.5:1. **Es el entregable de verdad de esta decisión**: si
  un ajuste futuro vuelve a bajar alguno de estos pares, este test lo
  detecta solo — no depende de que alguien vuelva a auditar a mano.
- `tokenParity.test.ts` sigue en verde — `tokens.ts` y
  `tokens.instrumento.css` coinciden.
- `npm test`, `npm run lint`, `npx tsc -b`, `npm run build` — todos en
  verde (317 tests, +10 sobre la línea base).
- Verificado en navegador de dev: los cinco tokens nuevos se reflejan en
  `getComputedStyle(document.documentElement)` en los dos modos, sin
  errores de consola.

**Ver también:** [DECISIÓN 039](decision039.md) — criterio de promoción que trajo
este hallazgo (originalmente D11 de la pasada 2) a `docs/decisiones/`.
[DECISIÓN 062](decision062.md) — Bloque C3, que introdujo `.pill.acc`, el
par nuevo encontrado en esta pasada.

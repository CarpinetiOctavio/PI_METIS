# DECISIÓN 043 — Contraste WCAG AA del tema Instrumento: hallazgos y propuesta, no aplicada
**Fecha:** 29 de Julio de 2026 (auditoría, pasada 2) — promovida a `docs/decisiones/` el 29 de Julio de 2026 (M1, pasada 3)
**Estado:** PENDIENTE DE DECISIÓN — Kevin/Octavio. Hallazgos y propuesta cerrados; los tokens no se tocaron.

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

### Propuesta concreta (no aplicada), calculada — mismo tono, oscurecido/aclarado lo mínimo necesario para llegar a 4.5:1

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
**Ninguna todavía — este es exactamente el punto de promover el hallazgo a
`docs/decisiones/`.** El tema Instrumento es identidad visual fijada; no se tocan
los tokens sin que Kevin/Octavio decidan explícitamente si aplicar la propuesta,
ajustarla, o aceptar el contraste actual como conocido y aceptado. Ninguna de las
dos pasadas de mejora (2 ni 3) tenía mandato para tomar esa decisión por su cuenta.

### Criterio de hecho
- `decision043.md` existe e indexada en `docs/decisiones/README.md`.
- `.claude/rules/sprint.md` ya no contiene la tabla de propuesta — solo una
  referencia de una línea a esta decisión.
- `tokens.instrumento.css` sin cambios.

**Ver también:** [DECISIÓN 039](decision039.md) — criterio de promoción que trajo
este hallazgo (originalmente D11 de la pasada 2) a `docs/decisiones/`.

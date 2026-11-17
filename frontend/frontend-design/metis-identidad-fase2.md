# METIS — Identidad Visual · Fase 2

**Estado:** exploración — cuatro direcciones en paralelo, sin decisión tomada.
**Compañero visual:** `metis-identidad-fase2.html` (explorador interactivo: cambiá tema y claro/oscuro para ver cada token aplicado en vivo).
**Fecha:** 20/07/2026 · Autores: Kevin / Octavio.

---

## Objetivo de la Fase 2

Dotar a METIS de una identidad propia, moderna y apropiada al dominio (análisis de frecuencia de eventos extremos hidrológicos), que lo aleje del look plano y utilitario de Excel e InfoStat sin caer en lo decorativo. La identidad debe sostener pantallas de datos densos (tablas de pruebas estadísticas, rankings de distribuciones, gráficos) y funcionar en modo docente y anónimo por igual.

Se exploran **cuatro direcciones** en modo claro y oscuro. Esta ronda no elige una: presenta el abanico para decidir con Octavio, igual que en la Fase 1 de wireframes.

---

## Reglas transversales (aplican a las cuatro direcciones)

### Blend institucional UCC

METIS tiene identidad propia. En las **secciones que incorporan el logo UCC** (ingreso institucional, pie de exportación PDF, encabezados oficiales), la identidad hace un *blend* hacia el **blanco/azul minimalista** de la marca universitaria. El objetivo es que el usuario entienda que la UCC está relacionada, sin que la marca institucional desplace a la de METIS.

- **Azul UCC:** `#00378A` (representativo — **confirmar contra el manual de marca oficial de la UCC**).
- **Modo claro:** panel blanco, tinta azul institucional (`#0B2545`), reglas finas azul claro.
- **Modo oscuro:** panel oscuro (`#0E1420`) con el azul UCC como acento, conservando el espíritu minimalista.
- El logo UCC nunca compite con el wordmark METIS: aparece en lockup lateral con una regla que los separa.

### Modo claro / oscuro

Las cuatro direcciones se entregan en ambos modos. El oscuro no es un simple "invertir": cada token se redefine para mantener contraste y jerarquía (ver tablas por dirección).

### Accesibilidad

- Texto principal sobre fondo apunta a contraste ≥ 4.5:1 (WCAG AA); títulos grandes ≥ 3:1.
- El estado de una prueba **nunca** se comunica solo por color: siempre acompaña una etiqueta (`aprobada` / `warning` / `crítico`). Esto es crítico para daltonismo y coherente con el principio de negocio "detecta y advierte".
- Los tres semáforos (ok / warn / crit) se eligieron con matices distinguibles también en escala de grises.

### Números como ciudadanos de primera clase

Todo estadístico, valor crítico, EEA y cuantil se renderiza en **monoespaciada** para alineación de columnas y lectura de cifras. Es una decisión transversal: METIS es, en el fondo, una máquina de números.

---

## Dirección 1 — Editorial de datos

**Concepto.** Estética de publicación científica moderna: serif de display para titulares, cuerpo sans muy legible, un acento sobrio y las cifras en monoespaciada como si fueran datos de portada. Serio, con autoridad, cómodo en tablas largas.

**Tipografía.** Titulares *Fraunces* (serif de contraste alto). Cuerpo *Inter*. Números *JetBrains Mono*.

**Movimiento.** Con carácter editorial: una regla acento (claret → dorada) **se dibuja** bajo el titular, papel rayado sutil de fondo, y las cifras de KPI en serif de gran tamaño como en una portada. En oscuro, doble lavado claret/dorado y un halo tenue en el wordmark — sensación de "manuscrito ilustrado", no de página vacía.

**Iconografía.** Trazo fino, esquinas rectas, sensación de grabado.

| Token | Claro | Oscuro |
|---|---|---|
| Fondo | `#FBF9F4` (papel cálido) | `#15110D` (negro cálido profundo) |
| Superficie | `#FFFFFF` | `#1E1913` |
| Tinta | `#1A1712` | `#F4EFE4` |
| Acento | `#8A2B3A` (claret) | `#E4949C` (claret rosado) |
| Acento 2 | `#9A6B1E` (dorado antiguo) | `#CBA25E` (dorado) |

**Cuándo conviene.** Si se prioriza la legibilidad de reportes y la sensación de "documento académico serio". Es la más cómoda para el PDF exportable.

---

## Dirección 2 — Hidrología / agua

**Concepto.** Azules y verdeazulados con gradientes suaves y movimiento orgánico que evoca el agua y el caudal. Formas redondeadas, amables. Conecta de inmediato con el objeto del proyecto sin ser literal (no hay gotas ni olas de clip-art).

**Tipografía.** Titulares *Space Grotesk* (geométrica con carácter). Cuerpo *Inter*. Números *JetBrains Mono*.

**Movimiento.** Gradiente que fluye lento en el hero sobre **washes de profundidad en capas**, una **waterline luminosa** al pie del hero, botones con degradé teal→cyan y barras de progreso que se llenan como una crecida. En oscuro, mar profundo con **glow** en tarjetas y logo (bioluminiscencia) — deja de ser un azul plano.

**Iconografía.** Trazo redondeado, esquinas suaves.

| Token | Claro | Oscuro |
|---|---|---|
| Fondo | `#F1F8FB` | `#03141A` (mar profundo) |
| Superficie | `#FFFFFF` | `#0B2732` |
| Tinta | `#0F2830` | `#E2F4F9` |
| Acento | `#0E7C93` (teal profundo) | `#3FD3EA` (cyan luminoso) |
| Acento 2 | `#3BB6CE` (cyan) | `#7CE9F5` |

**Cuándo conviene.** Si se busca que la identidad "cuente el dominio" a primera vista y diferenciarse fuerte de cualquier planilla. Riesgo: el azul institucional UCC y el teal del tema deben coordinarse para no competir en las secciones con logo.

---

## Dirección 3 — Académico moderno y sereno

**Concepto.** Neutros suaves, un azul académico sereno y mucho aire. Grotesca humanista, jerarquía clara, cero ruido. Transmite rigor y confianza sin rigidez — el registro justo para una defensa de grado ante tribunal y para el uso docente.

**Tipografía.** Titulares y cuerpo *Inter* (pesos distintos para jerarquía). Números *JetBrains Mono*.

**Movimiento.** Serena pero con relieve: lámina con textura de puntos muy sutil, una **franja de acento** vertical (azul → verde) al costado del hero, secciones que aparecen de abajo hacia arriba y tarjetas con elevación real. En oscuro, el fondo vira a un azul-carbón profundo con lavados de acento y KPI con degradé — deja de ser gris plano.

**Iconografía.** Trazo de línea uniforme, neutral.

| Token | Claro | Oscuro |
|---|---|---|
| Fondo | `#F4F7FA` (neutro con tinte frío) | `#0F141B` (azul-carbón profundo) |
| Superficie | `#FFFFFF` | `#161D27` |
| Tinta | `#1E262D` | `#E9EFF5` |
| Acento | `#2F6191` (azul académico) | `#72A6E2` |
| Acento 2 | `#2C8A6E` (verde sereno) | `#5FC4A4` |

**Cuándo conviene.** La apuesta más segura y de menor riesgo. Su azul convive naturalmente con el blend UCC (misma familia fría). Puede sentirse "poco distintivo" frente a las otras tres.

---

## Dirección 4 — Instrumento de precisión

**Concepto.** Alto contraste, retícula técnica, monoespaciada en los títulos y un acento de señal que resalta el dato vivo. Se siente como un instrumento de medición serio. Es la que más rotundamente rompe con Excel. Brilla en oscuro; el claro conserva la precisión.

**Tipografía.** Titulares *JetBrains Mono* (monoespaciada de display). Cuerpo *Inter*. Números *JetBrains Mono*.

**Movimiento.** Línea de escaneo con glow, cursor que parpadea y contadores que suben hasta clavar el estadístico. **Esquinas tipo corchete (HUD)** en las tarjetas, badge que **pulsa como un "REC"** en vivo, botones con halo de señal. En oscuro suma **scanlines tipo CRT** y **glow neón** en las cifras — feedback de máquina, ideal para el stream SSE.

**Iconografía.** Trazo grueso, esquinas biseladas, aire de HUD técnico.

| Token | Claro | Oscuro |
|---|---|---|
| Fondo | `#F3F6F8` | `#090C10` (negro instrumento) |
| Superficie | `#FFFFFF` | `#12171F` |
| Tinta | `#0B0E12` | `#E6EDF3` |
| Acento | `#0E7490` (cyan-azul) | `#22D3EE` (cyan señal) |
| Acento 2 | `#4D7C0F` | `#C6F84E` (lima señal) |

**Cuándo conviene.** Si se quiere que el diferenciador sea la potencia técnica del motor y que el análisis en vivo se sienta como un instrumento corriendo. Riesgo: para un ingeniero civil no experto puede leerse "demasiado de programador" — mitigable usándolo con moderación o reservándolo al modo experto.

---

## Principios de movimiento (transversales)

1. **El movimiento comunica estado, no adorna.** Cada animación mapea a un evento real del pipeline SSE (progreso, resultado de una prueba, pausa por atípico).
2. **Contadores que suben hasta el resultado.** El estadístico "se calcula a la vista" — refuerza que hay un motor real, no una planilla estática. (Ya prototipado en la Fase 1, Stream variante G.)
3. **Duraciones cortas y easing de salida** (`cubic-bezier(.2,.7,.2,1)`): rápido al inicio, desacelera al llegar. Se siente responsivo, no lento.
4. **Respetar `prefers-reduced-motion`** en la implementación real: quien lo pida, ve el estado final sin animación.

---

## Iconografía

Un único set de íconos, con el **trazo** ajustado por dirección (fino/editorial, redondeado/agua, uniforme/académico, grueso-biselado/instrumento). Cobertura mínima para V1.0: serie temporal, tendencia, independencia/correlación, tabla de resultados, distribución/ajuste, exportar, atípico, warning. Se dibujan como SVG con `currentColor` para heredar el acento del tema.

---

## Criterios para elegir la dirección (para la charla con Octavio)

| Criterio | Editorial | Hidrología | Académico | Instrumento |
|---|---|---|---|---|
| Diferenciación vs Excel/InfoStat | Media-alta | Alta | Media | **Muy alta** |
| Apto para tribunal / defensa | **Alta** | Media | **Alta** | Media |
| Convivencia con blend UCC (azul) | Media | Media (a coordinar) | **Alta** | Alta |
| Legibilidad para no expertos | **Alta** | Alta | **Alta** | Media |
| Fuerza en el stream en vivo | Media | Alta | Media | **Muy alta** |
| Riesgo | Bajo | Medio | **Muy bajo** | Medio-alto |

**Combinaciones posibles** que no hay que descartar: una base **Académica** (segura, convive con UCC) con **acentos de Instrumento** en el análisis en vivo y **cifras editoriales** en los reportes. La Fase 3 es justamente para mezclar y afinar.

---

## Próximos pasos

1. Elegir 1-2 direcciones finalistas (o una combinación).
2. Confirmar el azul institucional UCC contra el manual de marca oficial.
3. Aplicar la(s) dirección(es) finalista(s) a las variantes de wireframe ganadoras de la Fase 1.
4. Fase 3: mezcla, ajuste fino de color/tipografía/movimiento y definición del design-system para implementación en React + TypeScript.

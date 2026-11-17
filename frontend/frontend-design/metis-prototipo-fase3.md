# METIS — Prototipo Fase 3: Mix & Match

**Qué es.** La fusión de las dos fases anteriores: los **wireframes** (Fase 1, estructura) vestidos con las **identidades visuales** (Fase 2, color/tipografía/movimiento), en un único prototipo interactivo donde se combinan libremente todos los ejes de decisión.

**Artefacto.** `metis-prototipo-fase3.html`.
**Fecha.** 20/07/2026 · Autores: Kevin / Octavio.
**Depende de.** `metis-wireframes-fase1-decisiones.md` (variantes elegidas) y `metis-identidad-fase2.md` (identidades).

---

## Los cinco ejes del Mix & Match

Desde la barra superior se combina, en vivo, cualquier valor de estos cinco ejes:

1. **Pantalla** — las 8 del flujo (puerta de entrada → historial).
2. **Variante** — por pantalla, la **elegida (★)** más hasta **2 alternativas**. No se incluyen todas las variantes de la Fase 1: solo la elegida y las más representativas, tal como se pidió para esta fase.
3. **Tema** — Editorial, Hidrología, Académico, Instrumento (las 4 identidades, con sus tratamientos enriquecidos).
4. **Claro / Oscuro**.
5. **Docencia / Anónimo** — cambia el badge, la navegación (historial solo en docencia) y, sobre todo, la presentación: en anónimo, las pantallas con desarrollo colapsan a "solo resultados" (Decisión D).

Todo se re-renderiza al instante al tocar cualquier eje. El panel derecho muestra la combinación actual y una nota de la variante.

---

## Variantes incluidas por pantalla

★ = elegida en Fase 1. Las demás son alternativas para comparar con la identidad puesta.

| # | Pantalla | Elegida ★ | Alternativas |
|---|----------|-----------|--------------|
| 1 | Puerta de entrada | A · Login + anónimo | B · Card central · C · Landing |
| 2 | Carga y configuración | H · Dos col + modo + params | B · Dos columnas simple · G · Hero + acordeón |
| 3 | Análisis en vivo | A · Timeline vertical | G · Barras con contador · B · Barra + feed |
| 4 | Resultados Etapa 1 | E · Resumen + tablero | A · Resumen + secciones · C · Tablero de gráficos |
| 5 | Paso a paso vs Experto | D · Acordeón de pasos | A · Apilado · C · Comparación |
| 6 | Ranking de distribuciones | D · Tarjetas cal/hidro | A · Tabla + selección · C · Tarjetas top-N |
| 7 | Eventos de diseño | B · Foco en período | A · Tabla + gráfico · C · Slider |
| 8 | Historial | B · Tarjetas resumen | A · Lista con filtros |

(La pantalla 8 tiene solo una alternativa porque en Fase 1 existían dos variantes.)

---

## Cómo se aplican las identidades a los wireframes

En Fase 1 los wireframes usaban una paleta de grises neutra fija. En Fase 3 **toda la interfaz se reconstruyó sobre tokens** (variables CSS): cada componente (tarjetas, botones, tablas, pills, gráficos, inputs) toma su color del tema activo. Cambiar de tema o de claro/oscuro reasigna los tokens y el mismo markup se re-viste.

**Tipografía propia por tema — en toda la página, no solo en los títulos:**

- **Editorial** — Fraunces (serif) en títulos y cuerpo. Números en JetBrains Mono.
- **Hidrología** — Space Grotesk en títulos, Manrope (sans redondeada) en el cuerpo. Números en JetBrains Mono.
- **Académico** — IBM Plex Sans en títulos y cuerpo (voz institucional/técnica). Números en JetBrains Mono.
- **Instrumento** — JetBrains Mono en todo (títulos, cuerpo y números): registro de terminal.

Además de color y tipografía, cada tema aporta su **carácter** también en las pantallas reales:

- **Editorial** — fondo de papel rayado sutil, cifras de KPI en serif, acento claret + dorado.
- **Hidrología** — washes de profundidad en capas + un **caustic de luz que se desplaza** (animado), waterline luminosa bajo la barra, botones y progreso con degradé teal→cyan, glow en oscuro.
- **Académico** — wash de acento + textura de puntos muy sutil, **borde-acento a la izquierda de las tarjetas**, marca en los eyebrows, elevación y **aparición fade-up**; en oscuro, azul-carbón.
- **Instrumento** — retícula técnica de fondo, esquinas tipo corchete (HUD) en las tarjetas, badge que pulsa; en oscuro, scanlines CRT suaves y glow neón en las cifras.

Los semáforos (ok / warning / crítico) se derivan de cada paleta manteniendo contraste, y **el estado nunca se comunica solo por color** (siempre con etiqueta) — coherente con la accesibilidad definida en Fase 2 y con el principio "detecta y advierte".

---

## Decisiones respetadas en el prototipo

- **Modo único (Decisión A, Fase 1):** el toggle Paso a paso / Experto aparece en Carga y configuración; las pantallas siguientes se muestran según ese modo.
- **Anónimo = UI Experto (Decisión D):** al pasar a Anónimo, la pantalla "Paso a paso" colapsa a solo resultados, no hay historial y el badge lo indica.
- **METIS no elige la distribución óptima:** las pantallas de Ranking muestran el orden por EEA y botones "Elegir"; ninguna se marca como "óptima/recomendada". La variante A del Ranking incluye el aviso explícito.
- **Puerta de entrada (Decisión C):** la pantalla 1 ofrece login/registro **y** acceso anónimo (variantes A/B), más la landing dedicada (C) como alternativa.

---

## Pendientes / próximos pasos

1. **Elegir tema finalista** (o combinación) mirando el prototipo con Octavio, ya sobre pantallas reales y no sobre un style-tile.
2. **Cerrar la forma del punto de entrada** (botón en login vs landing) — sigue pendiente de Fase 1.
3. **Confirmar el azul institucional UCC** contra el manual de marca para las secciones con logo.
4. **Ajustes finos** (el corazón de esta fase): una vez elegido el tema, calibrar intensidad de motion, contraste y densidad por pantalla.
5. Combinaciones híbridas a evaluar: base **Académica** + acentos de **Instrumento** en el análisis en vivo + cifras **Editoriales** en reportes.

---

## Registro de versiones

| Versión | Cambios |
|---|---|
| v1 | Prototipo Mix & Match inicial: 8 pantallas (elegida + hasta 2 alternativas) × 4 temas × claro/oscuro × docencia/anónimo. |
| v2 | Tipografía propia por tema en toda la página (Fraunces / Space Grotesk+Manrope / IBM Plex Sans / JetBrains Mono). Hidrología con caustic animado + profundidad; Académico con wash de acento, borde-acento y fade-up. |

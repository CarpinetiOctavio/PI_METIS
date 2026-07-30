# METIS — Fase 1 (Wireframes): Decisiones de Diseño

**Propósito.** Registrar qué variante de wireframe se eligió para cada pantalla y **por qué**, más las decisiones de arquitectura de UI que surgieron de la revisión. El objetivo es de trazabilidad: ante el tribunal de ISI, cada decisión de interfaz debe poder justificarse, no aparecer "porque sí".

**Participantes.** Kevin Massholder, Octavio Carpineti.
**Fecha de la revisión.** 20/07/2026.
**Artefacto asociado.** `metis-wireframes-fase1.html` (explorador interactivo, v6 — cada pantalla se abre en su variante elegida, marcada con ★). Versiones previas archivadas en `frontend-design/versiones/`.
**Estado.** Selección de pantallas cerrada (20/07/2026). Queda pendiente la **forma** del punto de entrada (Decisión C).

**Criterio de cierre.** Para las pantallas donde Octavio se pronunció explícitamente (1, 2, 3) se usa su elección; para las que no mencionó (4, 5, 6, 7, 8) se usa la elección de Kevin. El Ranking (6), que Kevin dejó como "C o D", se resuelve en **D** — ver nota al pie de la tabla.

---

## Decisión de arquitectura A — El modo de presentación se elige una sola vez

**Decisión.** El **modo de presentación (Paso a paso / Experto)** se elige **una única vez, en la pantalla de Carga y configuración**, antes de ejecutar cualquier etapa. Es **inmutable durante el análisis**: toda la UI de las etapas siguientes (stream en vivo, resultados de Etapa 1, eventos de diseño, exportación) se renderiza **en función del modo elegido**. No se puede alternar a mitad de camino.

**Justificación.**
- Permitir cambiar el modo en cada paso obligaría a un layout que soporte ambas presentaciones simultáneamente en cada pantalla — complejidad innecesaria ("un bardo innecesario", en palabras de Octavio) para software cuyo foco es el cálculo.
- Un único toggle al inicio mantiene cada pantalla posterior enfocada y sobria: el usuario ve una sola UI coherente, no una que muta.
- **Coincide con la especificación existente:** el campo `modo` viaja en el request de `POST /api/v1/analysis/stream` (`.claude/rules/architecture/api-contracts.md`), es decir el modo ya está pensado para fijarse al iniciar el análisis, no por paso. La tabla de casos de uso de `CLAUDE.md` también trata "Modos: Paso a paso / Experto" como atributo del análisis (CU-01), no como conmutador por pantalla.

**Alternativa evaluada y descartada.** Selector de modo por paso / conmutable en cualquier momento. Descartada por complejidad de layout y por contradecir el contrato de API. 

**Consecuencia de diseño.** La pantalla de Carga y configuración debe exhibir el toggle Paso a paso / Experto de forma clara (implementado en la variante H). Las pantallas de resultados y del stream se diseñan en dos presentaciones — con desarrollo de fórmulas (paso a paso) vs. resultado directo (experto) — pero el usuario solo ve la que corresponde a su elección.

> Nota: el modo Paso a paso / Experto aplica a **CU-01 (docencia)**. En **CU-02 (anónimo)** no hay elección: es siempre "solo resultados" (ver `metis-wireframes-fase1.html`, pantalla "Paso a paso vs Experto", y la doc de la Fase 1 sobre la distinción docencia↔anónimo).

---

## Decisión de arquitectura B — Sobriedad sobre lo barroco

**Principio rector.** Ante la duda entre una variante recargada y una sobria, se elige la sobria. "Una interfaz barroca con algo que es cálculos choca" — la naturaleza del producto (validación estadística, análisis de frecuencia) pide una interfaz que no compita con el dato. Este criterio guía todas las selecciones de abajo y las de la Fase 2 (identidad visual).

---

## Decisión de arquitectura C — Punto de entrada: login / registro / anónimo

**Decisión.** La aplicación **abre en una puerta de entrada** donde el usuario elige explícitamente cómo entrar: **iniciar sesión** (cuenta @ucc.edu.ar), **registrarse**, o **entrar como anónimo / invitado**. No abre directo a la carga de datos ni a una landing puramente informativa.

**Forma (pendiente de elegir).** Dos maneras válidas, ambas prototipadas en la pantalla 1:
- **Botón "Entrar como anónimo" en la página de login** (variantes A y B). *Recomendada por simplicidad.*
- **Landing / puerta dedicada** con las tres opciones separadas y el trade-off explicado (variante C, nueva).

**Justificación.** El modo anónimo existe para **saltarse el overhead de loguearse** (así está en los requerimientos). Debe ser alcanzable sin cuenta, pero sin ocultar el camino con cuenta. Abrir directo a la carga escondería la existencia de la cuenta (historial, docencia, exportación); abrir en la puerta hace explícita la elección.

## Decisión de arquitectura D — El modo anónimo usa la UI de Experto

**Decisión.** El modo **anónimo presenta la misma UI que el modo Experto**: solo resultados, **sin explicaciones ni desarrollo paso a paso**. El anónimo **no puede** usar el modo Docencia (paso a paso) ni **exportar** el output. Es una herramienta de **checkeo rápido**.

**Consecuencia.** La presentación "solo resultados" de CU-02 (anónimo) **es** la presentación Experto de CU-01. La única presentación con fórmulas desarrolladas es Docencia + Paso a paso. En términos de UI hay **dos presentaciones reales**: *con desarrollo* (docencia paso a paso) y *solo resultados* (docencia experto ≡ anónimo).

> **Recordatorio (Facundo vía Octavio):** METIS **no elige la distribución óptima**. Presenta el ranking por EEA y **el usuario decide**. Las pantallas de Ranking usan botones "Elegir" y no etiquetan ninguna como "óptima / recomendada / ganadora", consistente con `.claude/rules/architecture/constraints.md` ("METIS no sugiere distribución ganadora — presenta el ranking, el usuario decide").

---

## Selección de variante por pantalla

| # | Pantalla | Variante | Elegida por | Motivo |
|---|----------|----------|-------------|--------|
| 1 | Puerta de entrada (login / registro / anónimo) | **A** (login + botón anónimo) · alt. **C** (landing) | Ambos + Octavio | Debe ofrecer login/registro **y** "entrar como anónimo" (Decisión C). Forma pendiente: botón en la página de login (A/B, recomendada) vs landing dedicada (C). |
| 2 | Carga y configuración | **H** (dos columnas + modo + parámetros) | Octavio | Prefirió la base **B** (más sobria) sobre la G. Se creó H = B + toggle Paso a paso/Experto (Decisión A) + partición de Cramer (de D) + indicador de personalización (de F). |
| 3 | Análisis en vivo (stream) | **A** (timeline vertical) | Octavio | "La opción 1", sobria; el usuario puede seleccionar cualquier paso ya hecho para desplegar su resultado. **Requisito:** pasos completados clickeables → detalle. |
| 4 | Resultados de Etapa 1 | **E** (resumen + tablero A+C) | Kevin | Octavio no la mencionó → se toma la elección de Kevin. |
| 5 | Paso a paso vs Experto | **D** (acordeón de pasos) | Kevin | Octavio no la mencionó → elección de Kevin. Compacta; escala bien a pruebas largas (Cramer). Con la Decisión A, esta vista se integra al flujo de resultados según el modo elegido. |
| 6 | Ranking de distribuciones | **D** (tarjetas + toggle calendario/hidrológico) | Kevin (†) | Kevin se inclinó por tarjetas (C o D). Se resuelve en **D** porque incorpora el toggle **año calendario / hidrológico**, y ese doble eje temporal es **obligatorio** para todo gráfico temporal según `.claude/rules/architecture/constraints.md`. La C no lo expone. |
| 7 | Eventos de diseño | **B** (foco en período) | Kevin | Octavio no la mencionó → elección de Kevin. |
| 8 | Historial | **B** (tarjetas resumen) | Kevin | Octavio no la mencionó → elección de Kevin. |

Todas las pantallas quedan **confirmadas**. (†) El Ranking se resolvió aplicando el requisito de doble eje temporal como criterio de desempate entre las dos opciones que Kevin barajaba.

---

## Detalle de la variante H (Carga y configuración)

Construida a partir del feedback puntual de Octavio sobre la pantalla 2:

- **Base B** — dos columnas (datos + preview a la izquierda, configuración a la derecha). Menos cargada que G.
- **Toggle Paso a paso / Experto** — destacado, con la leyenda "se elige una vez · define la UI de todas las etapas" (materializa la Decisión A). Presente solo en docencia; en anónimo se reemplaza por la etiqueta "solo resultados".
- **Parámetros avanzados** — sección con la partición de Cramer (tomada de la variante D). Al elegir "Personalizada", se muestran los campos n1% / n2% con sus valores, como en la variante F, más un indicador "Cramer personalizada".
- Corrige la observación de que la variante G "le faltaba el modo experto o docencia".

---

## Pendientes / próximos pasos

1. **Prototipar la Decisión A end-to-end:** que el explorador muestre cómo cambia la UI de resultados/stream según el modo elegido en config (hoy el modo se documenta y se elige en H, pero las pantallas posteriores aún no divergen visualmente por modo en el prototipo).
2. **Implementar el requisito de la pantalla 3:** en la variante A del stream, los pasos completados deben ser clickeables para desplegar el detalle de su resultado (hoy el detalle está anidado pero no como interacción de clic).
3. **Aplicar la identidad visual** (Fase 2) sobre estas 8 variantes elegidas una vez definida la dirección.
4. **Formalizar** la decisión de modo único como `docs/decisiones/decisionNNN.md` en el repositorio principal si el equipo lo considera (elegir número libre — 035 está reservado para protección de ramas según `sprint.md`).

---

## Registro de versiones del prototipo

| Versión | Cambios |
|---|---|
| v1 | 25 variantes iniciales, 8 pantallas, toggle docencia/anónimo. |
| v2 | +5 variantes mezcla (Config G, Stream G, ResultadosE1 E, Ranking D, Eventos C). |
| v3 | +pantalla "Paso a paso vs Experto" (4 variantes). |
| v4 | +Config variante H (esta revisión con Octavio) + este documento de decisiones. |
| v5 | Selección de variantes cerrada: cada pantalla marcada con ★ y abierta en su variante elegida. |
| v6 | Punto de entrada: login A/B + "entrar como anónimo" y nueva variante C (landing). Decisiones C y D (anónimo = UI Experto) + recordatorio de ranking. |

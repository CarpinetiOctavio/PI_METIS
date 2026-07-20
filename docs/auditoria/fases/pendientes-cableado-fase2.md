# Pendientes de cableado — Fase 2

Punto único de referencia para retomar en una sesión dedicada de core/.
No se implementa nada acá — solo se consolida qué queda abierto y dónde
está documentado cada uno, para no tener que rastrear varios archivos.

## Riesgo de corrección (prioridad alta)

**Orden cronológico no garantizado en `calcular_cramer`.** El contrato
detecta desorden (`CONTRACT_WRONG_ORDER`) pero hoy es warning no
bloqueante — Cramer opera sobre `arr[-n_w:]` sin validar que sea
realmente orden cronológico. Facundo confirmó (primeras reuniones,
recordado por Octavio, no registrado con precisión en su momento) que
las series siempre vienen en orden cronológico como garantía de
dominio — decisión tomada en consecuencia: elevar a bloqueante, sin
afectar el tratamiento de datos faltantes. Sin test que ejercite el
caso hoy. **Ver [DECISIÓN 030](../../decisiones/decision030.md) —
pendiente de implementar.** Implica actualizar CLAUDE.md, architecture.md y
constraints.md ("único caso: n<10" deja de ser cierto).

## Deuda de mantenibilidad (sin riesgo numérico verificado hoy)

**Refactor de cableado de Etapa 2, pendiente desde el cierre de la
2da auditoría de fidelidad (Bloque 3).** Dos consolidaciones sin
hacer, verificadas como matemáticamente correctas en su forma actual
pero duplicadas:
- `_skewness` (g, IV-4/IV-5) reimplementada de forma privada en 5
  archivos (`gamma3p.py`, `gen_pareto.py`, `gve.py`, `logpearson3.py`,
  `lognormal3p.py`), sin importar la versión ya verificada de
  `descriptive.py`.
- M̂0/M̂1/M̂2 (momentos de probabilidad pesada) con 3 estilos de
  indexado distintos (`gve.py`, `gamma2p.py`, `gumbel.py`), sin fuente
  compartida.

**Ver [DECISIÓN 022](../../decisiones/decision022.md) — pendiente de implementar.**

## Origen — pendientes heredados de Fase 1 (fidelidad a la tesis)

Los dos puntos de arriba (orden en Cramer, duplicación de código
genérico) fueron identificados durante la auditoría de Fase 1 y
formalmente traspasados a Fase 2 como insumo — este archivo es la
materialización real de ese traspaso, referenciado por nombre en
`fase1-unitarias.md` y en `decision022.md` desde el 10/07/2026 pero
nunca redactado hasta esta sesión (18/07/2026).
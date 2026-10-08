# Hallazgo: la planilla de la tesis calcula U_T con F en lugar de 1 − F (explica la "Causa C")

**Fecha:** 8 de octubre de 2026. **Autores:** Kevin, con Claude.
**Veredicto:** **CONFIRMADO numéricamente** sobre los valores publicados en la tesis. Falta la confirmación
de Facundo sobre la celda de su planilla (pregunta en `../pendientes/pendientes-facundo.md`).
**Qué cambia en METIS:** nada. METIS ya aplica la ecuación que escribe la tesis (IV-105). Lo que cambia es
la clasificación de las discrepancias de la auditoría: dejan de ser una pregunta abierta sobre METIS.
**Cómo se encontró:** en la comparación con otras herramientas pedida por Carlos Catalini
(`../comparacion-herramientas/README.md`, sección 4).

---

## 1. El problema que resuelve

La consolidación de la fase 4 (`../regresion/regresion-e2e-coreEstadistico/consolidacion-e2e.md` §4) dejó
como "la pregunta que más necesita resolverse" la **Causa C**: en Normal, Log-Normal 2p y 3p, Gamma 2p y
3p y Log-Pearson III, el EEA y los cuantiles de METIS divergen de la tesis aun cuando los parámetros
coinciden, en las 9 estaciones, creciendo con T. Las reconstrucciones del 10/07/2026 ya habían mostrado
que el EEA de la tesis "no sale de aplicar la fórmula documentada a sus propios parámetros", pero no se
sabía qué hacía la planilla en su lugar. La consecuencia práctica era la **Causa D**: en est_05 y est_08
esa divergencia cambia el orden del ranking.

Todas las familias afectadas comparten una sola pieza: la variable normal estándar U_T, que entra
directamente en Normal y Log-Normal (IV-101, IV-109, IV-120) y a través de Wilson-Hilferty en Gamma y
Log-Pearson (IV-135, IV-144, IV-260). Las familias que no la usan (Gumbel, GVE, Exponenciales, Uniforme)
coinciden con la tesis al redondeo.

## 2. Qué dice la tesis y qué hace la planilla

La tesis calcula U_T con la aproximación racional de Abramowitz y Stegun (26.2.23), IV-102 a IV-105:

```
Para 0 < F ≤ 0,5:   V = sqrt(ln(1/F²))                                       (IV-103)
                    UT = V − (b0 + b1·V + b2·V²) / (1 + b3·V + b4·V² + b5·V³)  (IV-102)
Para 0,5 < F ≤ 1:   usar 1 − F en V y cambiar el signo de UT                 (IV-105)
```

La aproximación solo es válida para probabilidades de cola entre 0 y 0,5. METIS la implementa así
(`core/etapa2/utils.py::_ut`, compartida por las 6 familias), y por eso coincide con la inversa exacta de `scipy` con
error < 0,015 %.

**La planilla, para F > 0,5, calcula V con F (no con 1 − F) y le cambia el signo.** Es decir, evalúa la
aproximación fuera de su dominio:

| T | F | U_T correcta | U_T de la planilla |
|---|---|---|---|
| 2 | 0,5 | 0,000 | 0,000 |
| 10 | 0,9 | 1,282 | 1,241 |
| 100 | 0,99 | 2,326 | 2,037 |

Como en T = 2 las dos coinciden, el error es invisible en el centro de la distribución y crece en la cola,
que es justamente la zona de los eventos de diseño.

## 3. Verificación

Para cada modelo elegido por Facundo de las familias afectadas se tomaron **los parámetros que imprime la
tesis** y se recalcularon los cuantiles con sus propias ecuaciones, una vez con U_T correcta y otra con la
U_T de la planilla (`../comparacion-herramientas/scripts/comparar.py`, sección H;
resultados en `comparacion_tesis_autoconsistencia.csv`):

| Estación, modelo | Diferencia máxima (T = 2 a 100) entre lo impreso y lo recalculado con U_T de la planilla | Con U_T correcta |
|---|---|---|
| est_01, Gamma 2p momentos-L | 0,002 % | 14,8 % |
| est_02, Log-Normal 3p MV | 0,004 % | 30,2 % |
| est_05, Log-Normal 3p MV | 0,010 % | 27,7 % |
| est_09, Normal momentos-L | 0,015 % | 5,6 % |
| est_07, Log-Normal 2p | 0,10 % | 15,5 % |
| est_03, Log-Pearson III indirecto | 0,36 % | 33,7 % |

En est_07 y est_03 la tesis imprime los parámetros con 3 cifras, y ese redondeo explica el residuo.

**EEA.** Con la U_T de la planilla, el EEA (IV-263, posiciones de Weibull) de Log-Normal 3p MV da 20,777 en
est_02 (tesis 20,799; con U_T correcta 29,551) y 5,764 en est_05 (tesis 5,784; correcta 8,770). En est_07
(Log-Normal 2p) y est_09 (Normal momentos-L) se acerca a la tesis sin cerrar del todo (3,837 contra 3,975;
2,809 contra 2,914): queda una diferencia menor sin explicar en esas dos, que no afecta la conclusión sobre
los cuantiles.

**METIS**, con sus propios parámetros, queda a ≤ 0,06 % del valor correcto en Normal y Log-Normal, y dentro
del error de Wilson-Hilferty (≤ 2,2 %) en Gamma y Log-Pearson.

## 4. Consecuencias

1. **La Causa C es un error de la planilla, no de METIS.** Las entradas de "Discrepancias en EEA sin
   explicación (Causa C)" y las de "Fórmulas con comportamiento no reproducible" que tratan cuantiles de
   estas familias (`../pendientes/pendientes-facundo.md`, por ejemplo "LN3p MV est_05, cuantiles no
   reproducibles con IV-120") quedan explicadas por este hallazgo, a reserva de la confirmación de Facundo.
2. **La Causa D tiene el mismo origen.** En est_05 y est_08 el ranking de la tesis difiere del de METIS
   porque el EEA de la tesis para esas familias está calculado con la U_T de la planilla.
3. **Los eventos de diseño publicados en la tesis para esos modelos subestiman el valor correcto**, más
   cuanto mayor es T: 30 % en est_02 y 28 % en est_05 para T = 100 (Log-Normal 3p MV, el modelo testigo
   o elegido en esas estaciones).
4. **METIS no cambia.** Reproducir el error de la planilla iría contra la regla del proyecto de seguir las
   ecuaciones escritas de la tesis (`formulas-etapa2.md`), igual que en la DECISIÓN 013.

## 5. Pregunta para Facundo

> En su planilla, ¿cómo se calcula U_T para F > 0,5? Si la celda usa F (y no 1 − F) dentro de
> V = √ln(1/F²), los cuantiles y el EEA de Normal, Log-Normal, Gamma y Log-Pearson de la tesis quedan
> desplazados hacia abajo en la cola: con ese cálculo se reproducen los valores publicados hasta la
> cuarta cifra significativa. ¿Confirma que IV-105 (usar 1 − F) es lo correcto?

## 6. Cómo reproducirlo

```bash
python docs/auditoria/comparacion-herramientas/scripts/correr_metis.py
python docs/auditoria/comparacion-herramientas/scripts/comparar.py   # sección H e I
```

Tablas: `docs/auditoria/comparacion-herramientas/resultados/comparacion_tesis_autoconsistencia.csv` y
`comparacion_tesis_eea.csv`. Figura: `resultados/figura_ut_planilla.png`.

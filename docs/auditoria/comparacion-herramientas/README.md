# Comparación de METIS con otras herramientas sobre las mismas series

**Fecha:** 8 de octubre de 2026.
**Origen:** pedido del director Carlos Catalini (08/10/2026): justificar el uso de METIS frente a las
alternativas que menciona la documentación (Excel, SAMHIA y otras) corriendo las mismas series en cada
una y verificando los resultados.
**Alcance:** las 9 series de caudales máximos medios diarios anuales de la tesis de Facundo Ganancias
Martínez (las mismas de la auditoría de las fases 1 a 4) y una serie mensual real de la UCC, la que SAMHIA
trae como ejemplo.

Este informe no reemplaza a la auditoría de fidelidad (`../fases/`, `../regresion/`): aquella pregunta si
METIS reproduce su fuente; esta pregunta qué obtiene un usuario con cada herramienta disponible cuando le
da la misma serie, y dónde y por qué los resultados difieren.

---

## Resumen

1. **Donde dos herramientas implementan la misma definición, METIS coincide con las librerías de
   referencia al redondeo de máquina.** Autocorrelación de Anderson (`stats::acf` de R), rachas de
   Wald-Wolfowitz (`randtests`), Mann-Kendall (`Kendall`, `trend`) y Kolmogorov-Smirnov (`stats::ks.test`):
   diferencia 0 en las 8 estaciones analizables. Gumbel por momentos-L y por máxima verosimilitud, GVE por
   máxima verosimilitud y Exponencial: diferencia de cuantiles de 0 a 0,0013 % contra `lmom` y `scipy`.
2. **Donde METIS difiere de una librería, la diferencia es una decisión documentada de la tesis, no un
   error:** la t de Student con varianza combinada n·Var (III-8), σ con n − 1 en Normal por máxima
   verosimilitud (IV-93), la aproximación de Thom para Gamma (IV-126) y Wilson-Hilferty para los cuantiles
   de la familia Gamma (IV-135, IV-144, IV-260). Cada una está cuantificada en la sección 3.
3. **Hallazgo: la "Causa C" que la auditoría de julio dejó abierta es un error de la planilla, no de
   METIS.** La planilla evalúa la aproximación racional de U_T (IV-102) con F en lugar de 1 − F cuando
   F > 0,5, contra lo que indica IV-105. Con esa regla se reproducen los cuantiles impresos de la tesis
   con un error de 0,004 % (sección 4). METIS aplica IV-105 y coincide con la inversa exacta.
4. **SAMHIA no es una alternativa para el análisis de frecuencia, sino una herramienta de diagnóstico
   exploratorio:** no ajusta distribuciones ni calcula eventos de diseño, y sus pruebas de independencia y
   homogeneidad son otras que las de la tesis. Con las mismas 8 series discrepa de METIS y de la tesis en 3
   veredictos de independencia y 1 de homogeneidad, siempre por una diferencia de definición (sección 5).
   Sobre la serie mensual corre las pruebas sobre los 304 valores mensuales, donde la independencia se
   rechaza con p < 10⁻²²; METIS agrega a 25 máximos anuales, que son independientes y homogéneos.
5. **Una hoja de cálculo con funciones nativas no reproduce la tesis:** `SKEW()`, `KURT()` y `CORREL()`
   no son las ecuaciones IV-5, IV-7 y III-1, y no hay funciones para Helmert, Cramer, la regla de bandas
   de Anderson ni los métodos de ajuste de la tesis. La comparación confirma además, por una vía
   independiente, la causa de la DECISIÓN 013: la asimetría que publica la tesis es la de `SKEW()`.

---

## Qué se comparó y cómo

| Herramienta | Qué es | Cómo se corrió | Qué cubre |
|---|---|---|---|
| **METIS** | Este proyecto | `backend/metis/core`, el mismo código de la aplicación (`ejecutar_etapa1`, `ejecutar_etapa2`, `calcular_eventos_diseno`) | Etapa 1 y Etapa 2 completas |
| **Planilla de Facundo** | Excel con el que se hizo la tesis (2010) | No se dispone del archivo: se usan los valores que publica la tesis, transcriptos en `../regresion/regresion-pipeline/` | 5 pruebas de Etapa 1, 13 distribuciones, eventos de diseño de los 2 modelos elegidos por estación |
| **Hoja de cálculo nativa** | Lo que obtendría un usuario de Excel con funciones integradas | `.xlsx` con fórmulas, recalculado con LibreOffice Calc 24.2.7 en modo headless (las funciones usadas tienen la misma definición en Excel) | Descriptiva, autocorrelación, t de mitades, cuantiles Normal, Log-Normal, Gamma y Gumbel por momentos |
| **Librerías de referencia** | Implementaciones independientes, revisadas y de uso extendido | R 4.3.3: `stats`, `randtests` 1.0.2, `Kendall` 2.2.2, `trend` 1.1.8, `lmom` 3.3 (Hosking). Python: `scipy` 1.13.0 | Bloques de cálculo sueltos: no traen los criterios de la tesis (bandas con tolerancia, jerarquías, Helmert, Cramer, EEA) |
| **SAMHIA** | Script de R del director Carlos Catalini (`SAMHIA_EST_v16.R`) | Sin modificar el script: un arnés (`scripts/correr_samhia.R`) le pasa los archivos y copia a una tabla los estadísticos que SAMHIA ya calcula | Descriptiva, gráficos, 7 pruebas propias, atípicos por banda K_n. Sin Etapa 2 |
| Hyfran-Plus | Software especializado (INRS, Quebec) | **No ejecutado:** licencia paga, no disponible | Ver comparación cualitativa, Libro §5.4.1 |
| Infostat | Software estadístico general (UNC) | **No ejecutado:** no tiene análisis de frecuencia de extremos | Ver Libro §5.4.2 |

**Reproducir** (desde la raíz del repo, con el entorno del backend, R con los paquetes de arriba y
LibreOffice):

```bash
python  docs/auditoria/comparacion-herramientas/scripts/correr_metis.py
Rscript docs/auditoria/comparacion-herramientas/scripts/referencia_r.R
python  docs/auditoria/comparacion-herramientas/scripts/hoja_calculo.py
# SAMHIA no se versiona (es código del director); desde una carpeta de trabajo:
Rscript .../scripts/correr_samhia.R ruta/SAMHIA_EST_v16.R .../resultados/samhia_resultados.csv est_01.xlsx ...
python  docs/auditoria/comparacion-herramientas/scripts/correr_metis_mensual.py ruta/UCC-DAT-ESR-AH-001-26-00.xlsx date P_IMERG
python  docs/auditoria/comparacion-herramientas/scripts/comparar.py
python  docs/auditoria/comparacion-herramientas/scripts/figura.py
```

Todos los números de este informe salen de los CSV de `resultados/`. Las series de las estaciones salen de
las fichas de regresión del repo; la serie mensual (`UCC-DAT-ESR-AH-001-26-00.xlsx`) es un registro de la
UCC aportado por el director y no se versiona.

---

## 1. Cobertura: qué puede hacer cada herramienta con la misma serie

| Capacidad | METIS | Planilla | Hoja nativa | Librerías | SAMHIA |
|---|---|---|---|---|---|
| Contrato de datos (n < 10 bloquea, orden cronológico, faltantes, negativos) | Sí | No (la tesis analiza est_09 con n = 7) | No | No | Parcial (salta n < 12) |
| Agregar una carga mensual o diaria a máximos anuales con mes de inicio configurable | Sí (DECISIÓN 057/065) | A mano | A mano | No | No (analiza los valores mensuales) |
| Las 8 pruebas de Etapa 1 con las ecuaciones y criterios de la tesis | 8 de 8 | 5 (sin Mann-Kendall, KS ni Chow) | Ninguna completa | Bloques sueltos, sin criterios | Otro conjunto de pruebas |
| Jerarquía de decisión (Anderson manda; Cramer decide; niveles crítico/normal) | Sí | Criterio del analista | No | No | No (p-valores sueltos) |
| Distribuciones y métodos de la tesis | 13 / 35 combinaciones | 13 / 34 | 4 por momentos | Momentos-L y MV estándar, no los de la tesis | Ninguna |
| Ranking por EEA sin sugerir ganadora | Sí | A mano | No | No | No |
| Eventos de diseño y gráficos de ajuste | Sí | Sí | Cálculo manual | Cálculo manual | No |
| Explicación paso a paso con la serie del usuario | Sí | No | No | No | No |
| Historial, decisiones registradas e informe PDF | Sí | No | No | No | PDF descriptivo |
| Verificación automática (tests, CI) | Sí | No | No | Propia de cada paquete | No |

---

## 2. Etapa 1

Valores en `resultados/comparacion_etapa1.csv`. "Tesis" es la planilla de Facundo.

| Prueba | METIS vs librería de referencia | METIS vs tesis |
|---|---|---|
| Anderson: r_k y lags fuera de banda | Idéntico en 8/8 (`stats::acf`, diferencia ≤ 6·10⁻¹⁶) | Idéntico en 9/9 |
| Wald-Wolfowitz: rachas y Z | Idéntico en 8/8 (`randtests::runs.test` con umbral en la media; su varianza es algebraicamente III-6) | Idéntico en 7/8; est_01 difiere (ver abajo) |
| Helmert S − C | Sin implementación de referencia | Idéntico en 7/8; est_01 difiere |
| Cramer t_w1, t_w2 | Sin implementación de referencia | Idéntico salvo donde la tesis redondea el 60 % distinto (est_05, est_07: Q1 de `consolidacion-e2e.md`) y est_01 |
| t de Student (mitades) | Difiere hasta 0,19 en t: R usa (n − 1)·Var en la varianza combinada; METIS, n·Var (III-8, confirmado por Facundo) | Idéntico con n par; con n impar la tesis toma `n1 = ceil(n/2)` y METIS `floor(n/2)` (Q16) |
| Mann-Kendall Z | Idéntico en 8/8 (`Kendall::MannKendall` y `trend::mk.test`) | La tesis no la publica |
| Kolmogorov-Smirnov Z | Idéntico en 8/8 (`stats::ks.test`, tipificado con A.57) | La tesis no la publica |

**est_01** es la estación donde la auditoría ya había detectado que la serie transcripta no es la que usó la
planilla (Q15 de `consolidacion-e2e.md`): METIS y R coinciden entre sí y ambos difieren de la tesis igual.

**Hallazgo menor sobre Q16.** La auditoría registró que la partición de t de Student para n impar "no
cambia ningún veredicto". Corriendo la función de METIS con `n1 = ceil(n/2)` se reproduce exactamente la t
de la tesis en las 4 estaciones con n impar (est_03, 05, 07, 08), y en **est_05 el veredicto individual sí
cambia**: la tesis da t = 2,082 > 2,0262 (rechaza) y METIS da t = 1,817 (aprueba). El nivel de homogeneidad
de METIS pasaría de `homogeneidad_ok` a `homogeneidad_warning`. Queda anotado en la pregunta Q16 de
`../pendientes/pendientes-facundo.md`, que deja de ser de prioridad baja.

---

## 3. Etapa 2

### 3.1 Contra la tesis: cuantiles de los modelos elegidos por Facundo

`resultados/comparacion_cuantiles_tesis.csv`. Diferencia máxima entre T = 2 y T = 100:

| Coinciden (≤ 0,02 %) | Difieren, crecen con T | Sin equivalente en METIS |
|---|---|---|
| Exponencial β (est_02), GVE MV (est_03, est_05, y est_04 en la columna rotulada "LP3 MMI"), Exponencial x0-β MV (est_06), Gumbel momentos-L (est_07, est_08), Uniforme (est_09) | Gamma 2p momentos-L (est_01, 17,6 %), Log-Normal 3p MV (est_02, 43,3 %; est_05, 38,3 %), Log-Pearson III indirecto (est_03, 54,1 %; est_04, 37,0 %), Log-Normal 2p (est_07, 18,2 %), Normal momentos-L (est_09, 6,0 %) | Gamma 3p por Momentos de Probabilidad Pesada (est_01, est_06, est_08): la tesis no desarrolla sus ecuaciones |

Todas las columnas que difieren son de familias cuyo cuantil depende de la variable normal estándar U_T.
La sección 4 explica por qué.

### 3.2 Contra librerías de referencia

Diferencia máxima de cuantiles entre T = 2 y T = 500, en las 8 estaciones analizables
(`comparacion_lmom.csv`, `comparacion_scipy_mle.csv`):

| Familia y método | Referencia | Diferencia máxima | Por qué |
|---|---|---|---|
| Gumbel, momentos-L | `lmom::pelgum` | 0 % | Misma fórmula (IV-188/189) |
| Normal, momentos-L | `lmom::pelnor` | 0,02 % | Aproximación racional de U_T (IV-102), error < 4,5·10⁻⁴ |
| GVE, momentos-L | `lmom::pelgev` | 0,20 % | La tesis usa la aproximación de κ de Hosking (1985), IV-235; `lmom` usa una más precisa |
| Gamma 2p, momentos-L | `lmom::pelgam` | 1,72 % | Wilson-Hilferty en el cuantil (IV-135) |
| Gumbel, máxima verosimilitud | `scipy.stats.gumbel_r.fit` | 0 % | Mismo estimador |
| GVE, máxima verosimilitud | `scipy.stats.genextreme.fit` | 0,001 % | Mismo estimador |
| Exponencial β | `scipy.stats.expon.fit` | 0 % | Mismo estimador |
| Normal, "máxima verosimilitud" | `scipy.stats.norm.fit` | 1,66 % | La tesis usa σ con n − 1 (IV-93); el estimador de MV usa n |
| Gamma 2p, máxima verosimilitud | `scipy.stats.gamma.fit` | 2,10 % | Aproximación de Thom (IV-126) más Wilson-Hilferty |

### 3.3 Las aproximaciones de la tesis, aisladas

Mismos parámetros de METIS; solo cambia la fórmula del cuantil por la inversa exacta de `scipy`
(`comparacion_aproximaciones.csv`). Es el error que METIS hereda por implementar las ecuaciones de la tesis
tal cual:

| Familia | Ecuación de la tesis | Diferencia máxima en T = 100 | En todo el rango T = 2 a 500 |
|---|---|---|---|
| Normal | IV-101/102 | 0,014 % | 0,015 % |
| Log-Normal 2p y 3p | IV-109, IV-120 | 0,06 % | 0,06 % |
| Gamma 2p | IV-135 (Wilson-Hilferty) | 0,24 % | 2,5 % (T = 2, forma β chica) |
| Gamma 3p | IV-144 | 0,23 % | 1,6 % |
| Log-Pearson III | IV-260 | 0,91 % | 8,7 % (T = 500, est_02 por MV, β = 1,18) |

Wilson-Hilferty pierde precisión con forma β chica (asimetría alta) y en los extremos. METIS sigue la tesis
porque es su fuente de verdad (`formulas-etapa2.md`); usar la inversa exacta es una mejora candidata para
la V2 que conviene consultar con Facundo, ya que cambiaría la reproducción de la tesis.

---

## 4. Hallazgo: la U_T de la planilla (la "Causa C")

La auditoría de julio (`consolidacion-e2e.md` §4) dejó abierta la pregunta más importante del proyecto: en
Normal, Log-Normal, Gamma y Log-Pearson los cuantiles y el EEA de METIS divergen de la tesis aunque los
parámetros coincidan, y no se podía decidir si el error era de METIS o del Excel sin tener el archivo.

**La comparación lo resuelve.** Tomando los parámetros que imprime la propia tesis y sus propias
ecuaciones de cuantil:

- con U_T correcta (IV-102 a IV-105, o la inversa exacta), el resultado coincide con METIS (≤ 0,06 % en
  Normal y Log-Normal);
- con U_T calculada como lo hace la planilla, el resultado coincide con lo que la tesis imprime.

La planilla evalúa la aproximación racional de Abramowitz y Stegun (IV-102), válida solo para
0 < p ≤ 0,5, con V = √ln(1/F²) usando F también cuando F > 0,5, y le cambia el signo. IV-105 indica usar
1 − F en ese tramo, que es lo que hace METIS. Para F = 0,99 (T = 100) la planilla obtiene U_T = 2,037 en
lugar de 2,326, y el error crece con T.

| Estación, modelo | Cuantil T = 100 impreso | Recalculado con U_T de la planilla | Recalculado con U_T correcta | METIS |
|---|---|---|---|---|
| est_02, Log-Normal 3p MV | 800,70 | 800,67 (0,004 %) | 1146,53 | 1147,22 |
| est_05, Log-Normal 3p MV | 268,51 | 268,49 (0,006 %) | 371,44 | 371,40 |
| est_09, Normal momentos-L | 47,72 | 47,72 (0,003 %) | 50,58 | 50,58 |
| est_01, Gamma 2p momentos-L | 495,11 | 495,11 (0,000 %) | 581,45 | 582,16 |
| est_07, Log-Normal 2p | 147,89 | 148,02 (0,09 %) | 174,97 | 174,87 |
| est_03, Log-Pearson III indirecto | 419,16 | 417,66 (0,36 %) | 632,53 | 646,04 |

En est_07 y est_03 el residuo se explica porque la tesis imprime los parámetros con 3 cifras. La tabla
completa, para todos los T, está en `comparacion_tesis_autoconsistencia.csv` y en la figura
`resultados/figura_ut_planilla.png`.

**El EEA tiene la misma causa.** Con la U_T de la planilla, el EEA de Log-Normal 3p MV da 20,78 en est_02
(tesis 20,80; con U_T correcta, 29,55) y 5,76 en est_05 (tesis 5,78; correcta, 8,77)
(`comparacion_tesis_eea.csv`). En est_07 y est_09 el EEA se acerca al de la tesis pero no cierra del todo
(3,84 contra 3,97; 2,81 contra 2,91): queda una diferencia menor sin explicar en esas dos.

**Consecuencias:**

1. La "Causa C" deja de ser una pregunta abierta sobre METIS: es un error de la planilla, y METIS aplica
   la ecuación que la propia tesis escribe. Las inversiones de ranking de est_05 y est_08 ("Causa D"), que
   dependen del EEA de esas familias, tienen el mismo origen.
2. Los eventos de diseño que publica la tesis para esos modelos subestiman el valor correcto, y más cuanto
   mayor es T (30 % en est_02 para T = 100).
3. Falta que Facundo lo confirme mirando la celda de U_T de su planilla; queda como pregunta en
   `../pendientes/pendientes-facundo.md`. El detalle del hallazgo está en
   `../hallazgos/hallazgo-ut-planilla-causa-c.md`.

---

## 5. SAMHIA

`resultados/comparacion_samhia.csv` y `samhia_resultados.csv`. SAMHIA corre sobre los valores tal como
llegan (sin agregar) y saltea series de menos de 12 datos (est_09).

| Aspecto | METIS (tesis) | SAMHIA | Efecto en las 8 estaciones |
|---|---|---|---|
| Independencia "Anderson" | Correlograma r_1 a r_{n/3} con bandas III-3 y tolerancia del 10 % | Correlación de Pearson de lag 1 y su p-valor | SAMHIA rechaza en est_02, est_03 y est_08; METIS y la tesis aceptan |
| Wald-Wolfowitz | Rachas respecto de la media (III-4) | `runs.test` con su umbral por defecto, la mediana | est_02 y est_06: METIS rechaza al 5 % con el mismo Z que la tesis, SAMHIA no |
| Homogeneidad | Helmert, t de Student y Cramer, con Cramer como prueba decisiva | Mann-Whitney y Mood entre mitades | est_08: METIS da homogeneidad crítica (Cramer rechaza el último 30 %), SAMHIA no detecta nada |
| Tendencia | Mann-Kendall y Kolmogorov-Smirnov | Mann-Kendall | Coinciden en 8/8 |
| Atípicos | Chow (Grubbs-Beck sobre logaritmos, 10 %) | Banda media ± K_n·S sobre los valores, K_n = 0,4083 ln N + 1,1584 | SAMHIA marca 1 o 2 puntos en 6 estaciones; Chow no marca ninguno |
| Etapa 2 | 13 distribuciones, EEA, eventos de diseño | No tiene | |

**Serie mensual (P_IMERG, 304 meses de 2000 a 2025).** SAMHIA corre las pruebas sobre los 304 valores
mensuales: Pearson de lag 1 con p = 4·10⁻²⁶, Wald-Wolfowitz p = 5·10⁻²³, Ljung-Box p ≈ 0. La serie
mensual no es independiente (estacionalidad), que es justamente por qué no sirve para un análisis de
frecuencia de extremos. METIS infiere la resolución mensual, recorta los años parciales, agrega a 25
máximos anuales (con el año hidrológico desde junio, como usa SAMHIA, o desde julio) y sobre esa serie las
8 pruebas aprueban: independiente, homogénea, apta para Etapa 2 (con la advertencia de n < 30).

Las diferencias no indican que SAMHIA esté mal: es una herramienta de diagnóstico multivariable
exploratorio, con otro propósito. Indican que sus veredictos no son intercambiables con los de la
metodología de la tesis, que es la que METIS automatiza.

**Relación con el alcance futuro de METIS.** `docs/sprint.md` ("Scope post-M5 — pruebas adicionales
confirmadas por Carlos") lista Durbin-Watson, Ljung-Box, Mann-Whitney, Mood, Spearman y K_n como pruebas a
incorporar: son exactamente las de SAMHIA. Esta comparación aporta evidencia para hacerlo como
complemento y no como reemplazo: sobre las mismas series llegan a otros veredictos que las pruebas de la
tesis en 4 casos, así que deberían mostrarse aparte, sin entrar en los niveles de independencia y
homogeneidad que hoy deciden si una serie pasa a Etapa 2.

---

## 6. Hoja de cálculo con funciones nativas

`resultados/comparacion_hoja_calculo.csv` (fórmulas en `hoja_calculo_formulas.xlsx`).

| Magnitud | Función nativa | Diferencia con METIS | Observación |
|---|---|---|---|
| Media, desvío | `AVERAGE`, `STDEV.S` | 0 | |
| Asimetría | `SKEW` | −3,5 % a −7,8 % según la estación | `SKEW` usa S con n − 1; IV-4/IV-5 usan la varianza sesgada. **La tesis publica el valor de `SKEW`** (est_02: 1,565), lo que confirma por otra vía la causa de la DECISIÓN 013 |
| Curtosis | `KURT` | −24 % a −119 %: es otra magnitud (exceso, otra corrección) | La curtosis de la tesis tampoco es IV-7: es IV-7 aplicada a una curtosis sesgada calculada con S de n − 1 (est_02: 4,219 = 4,594 × (23/24)², donde 4,594 es la curtosis sesgada de IV-6), el mismo origen que la asimetría |
| Autocorrelación lag 1 | `CORREL` desplazado | −1,7 % a 4,8 % | `CORREL` usa la media de cada tramo; III-1 usa la media global y el denominador completo |
| p-valor t de mitades | `T.TEST` | Igual al de R | Ver sección 2: la t de la tesis no es la de `T.TEST` |
| Cuantiles Normal, Log-Normal | `NORM.INV`, `LOGNORM.INV` | ≤ 0,06 % | Las inversas nativas son exactas; METIS usa IV-102 |
| Cuantil Gamma 2p | `GAMMA.INV` | ≤ 2,5 % | Wilson-Hilferty (sección 3.3) |
| Cuantil Gumbel | Fórmula IV-199 | 0 | |

Una hoja de cálculo sirve para cuentas sueltas, pero no tiene funciones para Helmert, Cramer, la regla de
bandas de Anderson, Chow con K_N, los métodos iterativos de la tesis ni el EEA: el usuario tiene que
construir cada uno a mano, que es exactamente el proceso que METIS automatiza y lo que dio lugar a los
errores de la planilla documentados en la sección 4 y en la DECISIÓN 013.

---

## 7. Qué justifica usar METIS, herramienta por herramienta

- **Frente a la planilla de Facundo.** Mismos métodos y misma fuente, con tres diferencias medibles: METIS
  reproduce los resultados correctos de la planilla (columnas que coinciden en la sección 3.1), no
  reproduce sus errores (U_T, asimetría con `SKEW`) porque sigue las ecuaciones escritas, y está verificado
  contra implementaciones independientes. Además valida el contrato (la tesis analizó est_09 con 7 datos) y
  automatiza la agregación temporal.
- **Frente a una hoja de cálculo genérica.** Las funciones nativas no implementan la metodología de la
  tesis; armarla a mano es el proceso propenso a errores que este proyecto reemplaza.
- **Frente a SAMHIA.** Son complementarias: SAMHIA hace diagnóstico exploratorio multivariable; METIS hace
  la validación y el análisis de frecuencia de la metodología de la tesis, que SAMHIA no cubre. Sobre las
  mismas series, SAMHIA llega a otros veredictos en 4 casos por usar otras pruebas, y sobre series
  mensuales analiza valores dependientes.
- **Frente a librerías de R o Python.** Son el respaldo de corrección de METIS (sección 3.2), no una
  alternativa para el usuario final: exigen programar, no traen los criterios de decisión de la tesis ni
  sus métodos de ajuste (Máxima Entropía, Mínimos Cuadrados, las variantes de Log-Pearson), y no tienen
  modo docente.

---

## 8. Limitaciones

- La planilla original no estuvo disponible: "tesis" son los valores publicados. El hallazgo de la
  sección 4 se demuestra numéricamente con esos valores, pero su confirmación definitiva requiere la celda
  de U_T del Excel.
- Hyfran-Plus e Infostat no se corrieron (licencia; alcance). La comparación con ellos sigue siendo
  cualitativa.
- Chow, Helmert y Cramer no tienen implementación de referencia en las librerías usadas: para esas tres
  pruebas la única comparación es contra la tesis.
- La serie mensual es una sola; la conclusión sobre SAMHIA y series mensuales se apoya en la propiedad
  general de la estacionalidad, que esa serie muestra con claridad.
- SAMHIA se corrió con R 4.3.3; el paquete `zyp`, que el script intenta cargar pero no usa en ningún
  cálculo, no estaba disponible.

---

## Archivos

| Archivo | Contenido |
|---|---|
| `scripts/series.py` | Lee las 9 series y los valores de la tesis desde las fichas de regresión |
| `scripts/correr_metis.py` | Corre el motor de METIS sobre las 9 series |
| `scripts/correr_metis_mensual.py` | Carga una serie mensual como lo hace la aplicación (parser, agregación, Etapa 1) |
| `scripts/referencia_r.R` | Implementaciones de referencia en R |
| `scripts/hoja_calculo.py` | Arma y recalcula la hoja con funciones nativas |
| `scripts/correr_samhia.R` | Arnés que corre SAMHIA sin modificarlo y captura sus estadísticos |
| `scripts/comparar.py` | Cruza todo y escribe las tablas `comparacion_*.csv` y `resumen.json` |
| `scripts/figura.py` | Figura del hallazgo de la sección 4 |
| `resultados/` | Entradas intermedias, tablas de comparación y figura |

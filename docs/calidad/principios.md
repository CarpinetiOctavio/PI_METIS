# Los siete principios del testing, aplicados a METIS

TP integrador de Calidad de Software, bloque B9. Cada principio (ISTQB) con un caso real del proyecto donde se vio
y la práctica que lo tiene en cuenta.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

## 1. El testing muestra la presencia de defectos, no su ausencia

**En METIS:** la auditoría de julio encontró los errores de GVE y Log-Normal 3p (D-08, D-09) en código que corría
sin fallar y devolvía números plausibles. Que nada fallara no decía nada sobre si el número era el de la tesis.
**Cómo se tiene en cuenta:** un test de exactitud compara contra el valor de la fuente, nunca contra la salida previa
del propio código (`plan-de-pruebas.md` §5.3). Que la suite pase no se presenta como prueba de que el motor es
correcto; la evidencia de exactitud es la auditoría y la comparación con otras herramientas.

## 2. El testing exhaustivo es imposible

**En METIS:** 13 distribuciones con hasta 6 métodos, tres resoluciones temporales, 12 meses de inicio de año, dos
tipos de variable, series con ceros, negativos o faltantes y cualquier longitud desde 10. Las combinaciones no se
pueden recorrer.
**Cómo se tiene en cuenta:** se eligen casos con técnicas (valores límite, clases de equivalencia, tablas de
decisión: `casos-de-prueba.md`) y se prioriza por riesgo (`riesgos.md`).

## 3. Testing temprano

**En METIS:** las fórmulas se auditaron contra la tesis antes de construir la interfaz (Fases 1 a 4). Un error de
fórmula encontrado ahí costó corregir una función; encontrado después, habría invalidado resultados ya mostrados a
los directores.
**Cómo se tiene en cuenta:** el resultado esperado se escribe antes del código (criterio de entrada de la unidad,
`plan-de-pruebas.md` §6.2); el gate exige tests del código nuevo en el mismo PR.

## 4. Agrupación de defectos

**En METIS:** de los 10 defectos registrados, 3 están en la agregación temporal (RF-GEN-P-10) y 2 en Etapa 2
(RF-GEN-P-08); las fórmulas que más hallazgos tuvieron en la auditoría son GVE, Log-Normal 3p y Generalizada de
Pareto (`trazabilidad.md`).
**Cómo se tiene en cuenta:** esos módulos tienen más tests por línea y sus propios documentos de hallazgos; Pareto,
donde todavía hay una inconsistencia sin resolver, se calcula pero no se puede elegir (DECISIÓN 074).

## 5. La paradoja del pesticida

**En METIS:** la suite del frontend llegó a 98 tests en verde con la aplicación rota (F1, D-01), porque todos
probaban el componente con el hook mockeado: repetir más tests del mismo tipo no iba a encontrarlo.
**Cómo se tiene en cuenta:** se agregaron tipos de prueba nuevos en lugar de más de los mismos: la Capa 2 (componente
y hook reales, red mockeada solo en el borde), los E2E contra el sistema desplegado, y los casos de caja negra
diseñados por técnica en lugar de por cobertura.

## 6. El testing depende del contexto

**En METIS:** el riesgo principal no es la carga ni la seguridad, sino un número de diseño incorrecto sin
advertencia. Por eso la mayor inversión está en el oráculo externo (tesis, otras herramientas) y no en, por ejemplo,
pruebas de penetración. Con un uso previsto de pocos docentes en la intranet, la carga se prueba para fijar una línea
de base y detectar degradaciones, no para dimensionar miles de usuarios.
**Cómo se tiene en cuenta:** las tres características prioritarias de `matriz-iso25010.md` salen del contexto de
uso, y lo justifica la sección 2 de ese documento.

## 7. La falacia de la ausencia de errores

**En METIS:** un motor sin errores que no responde lo que el usuario necesita no sirve. Pasó con los eventos de
diseño de una serie mensual: Carlos observó que hablaban de años aunque la serie cargada fuera mensual (DECISIÓN
076). El cálculo era correcto (Etapa 2 ajusta los máximos anuales, así que T está en años), pero la pantalla no decía
qué valor se había analizado. No había ningún defecto; el resultado no comunicaba lo que significaba.
**Cómo se tiene en cuenta:** la revisión de los directores en uso real es parte del control (`qa-vs-qc.md` §2), y la
completitud respecto del Manual de Requerimientos se mide aparte de los defectos (`trazabilidad.md`).

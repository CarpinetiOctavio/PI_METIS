# Autoría y aportes de los integrantes

**Fecha:** 17 de noviembre de 2026. Se agrega a pedido de Octavio Carpineti.

El historial de git de METIS registra quién escribió cada línea de código y de documentación, pero no quién relevó
el problema que la motivó, quién coordinó las consultas con los directores ni qué trabajo se hizo fuera del
repositorio. Este documento reúne esas tres cosas con su fuente, para que el aporte de cada integrante no se lea
solamente a partir de los commits. Complementa la sección "Distribución del trabajo" del informe final (Tabla 24),
que mide la autoría con `git blame`.

## 1. Etapas del trabajo

Octavio Carpineti hizo sus commits entre el 04/05/2026 y el 09/09/2026: la estructura del repositorio, los modelos
de datos, la autenticación, el motor estadístico de las dos etapas, la primera integración continua, las cuatro
fases de auditoría contra la tesis y las correcciones de fórmulas de la Etapa 2 de agosto y septiembre. Kevin
Massholder hizo sus commits desde el 22/07/2026: el cliente web, la integración de punta a punta, lo agregado al
servidor desde agosto, la infraestructura de calidad y el despliegue en la UCC.

## 2. Métricas del repositorio

Medidas sobre `staging` el 17/11/2026.

| Medida | Octavio Carpineti | Kevin Massholder |
|---|---|---|
| Commits propios, sin integraciones | 53 | 396 |
| Líneas insertadas en esos commits | 33.082 | 123.072 |
| Pedidos de incorporación abiertos | 22 | 120 |
| Decisiones creadas (`docs/decisiones/`) | 39 (001 a 034, 060, 061, 068, 069 y 070) | 44 |
| Líneas de `docs/auditoria/pendientes/pendientes-facundo.md` | 889 de 1.227 | 301 de 1.227 |

Tres commits figuran con autor "Claude", y 37 líneas de `pendientes-facundo.md` se le atribuyen a ese autor.

Autoría de las líneas vigentes por área, con `git blame -w -M -C -C`. Esta variante sigue las líneas movidas o
copiadas entre archivos, así que un refactor no le transfiere la autoría a quien lo hizo. La diferencia con el
`git blame` simple es de 0 a 7 puntos según el área.

| Área | Líneas | Octavio Carpineti | Kevin Massholder |
|---|---|---|---|
| `backend/metis/core/` (motor estadístico) | 5.390 | 73 % | 27 % |
| `backend/metis/core/etapa2/` | 2.813 | 96 % | 4 % |
| `backend/metis/core/etapa1/` | 842 | 62 % | 38 % |
| `backend/metis/auth/` | 594 | 61 % | 39 % |
| `backend/metis/services/` | 1.861 | 28 % | 72 % |
| `backend/metis/api/` | 858 | 18 % | 82 % |
| `backend/tests/` | 12.768 | 23 % | 77 % |
| `docs/auditoria/` | 18.500 | 81 % | 11 % |
| `.claude/rules/` (reglas y fórmulas) | 3.977 | 58 % | 41 % |
| `docs/decisiones/` | 9.032 | 36 % | 64 % |

En `docs/auditoria/` el 7 % restante se atribuye a "Claude"; en `.claude/rules/`, el 1 %.

Las cifras miden autoría, no esfuerzo ni dificultad. Tampoco registran las revisiones de código: GitHub no tiene
ninguna revisión formal en los 142 pedidos de incorporación, aunque el informe final indica que Octavio Carpineti
participó como revisor de los cambios desde el 01/10/2026. Lo hecho fuera de git se detalla en la sección 5.

## 3. Relevamiento de pendientes y consultas a los directores

**Octavio Carpineti:**

- creó `docs/auditoria/pendientes/pendientes-facundo.md` el 18/07/2026 (`5e9edaf`), al cierre de la auditoría del
  motor estadístico, y redactó la mayor parte de sus preguntas:
  - la partición de Cramer (DECISIÓN 011) y la fórmula de asimetría (DECISIÓN 013);
  - las fórmulas de la Etapa 2 que no se reproducen (Generalizada Exponencial, Log-Pearson III, Log-Normal 2p y 3p,
    Gamma 3p y GVE);
  - las discrepancias de EEA;
  - el valor crítico de una o dos colas en Cramer y en t de Student;
  - el valor crítico de Mann-Kendall para n = 7;
  - los métodos ME y MC en otras distribuciones;
  - el comportamiento ante ceros de cinco distribuciones;
- verificó la ecuación IV-153 de la Generalizada de Pareto por Mínimos Cuadrados: consiguió la confirmación de
  Carlos Catalini (`4ea53f2`) y cerró el tema con la DECISIÓN 068 (`51bef0a`, `b7ff241`, `074c22d`);
- planteó la pregunta sobre la partición de t de Student con n impar, que surge de la Q16 de su consolidación de la
  fase 4 (`docs/auditoria/regresion/regresion-e2e-coreEstadistico/consolidacion-e2e.md`);
- redactó el "Consolidado de pendientes y decisiones de la auditoría del motor estadístico" (versión 3,
  09/09/2026), el documento que respondieron los directores;
- según el plan de reparto, quedó a cargo de enviarlo y de hacer el seguimiento con Facundo Ganancias Martínez y
  Carlos Catalini (sección 5).

**Kevin Massholder:**

- relevó las preguntas sobre agregación temporal (R0.1 a R0.3) que el consolidado sumó a las de la auditoría;
- encontró la inconsistencia de convenciones de signo de la Generalizada de Pareto (01/10/2026, `518b7b3`,
  `docs/auditoria/hallazgos/hallazgo-gen-pareto-convenciones.md`);
- relevó la U_T de la planilla (08/10/2026, `c9fcce0`) y las colas de Mann-Kendall (20/09/2026, H-2 de
  `docs/auditoria/fases/auditoria-formulas-latex.md`).

**Respuestas.** Facundo Ganancias Martínez respondió el consolidado el 22/10/2026. El 29/10/2026 respondió las
cuatro preguntas que habían quedado abiertas: la U_T con F > 0,5, las convenciones de la Generalizada de Pareto, la
partición de t de Student con n impar y las colas de Mann-Kendall. Con la respuesta sobre Pareto, la distribución
quedó fuera del cálculo de la v1 y su módulo pasa a la v2 (addendum del 29/10/2026 a la DECISIÓN 074).

## 4. Implementación de las respuestas

Kevin Massholder implementó y documentó los cambios que surgieron de las respuestas a preguntas relevadas por Octavio
Carpineti. En git figuran como commits suyos y no mencionan el relevamiento que los originó:

| Commit | Fecha | Cambio | Pregunta de origen |
|---|---|---|---|
| `4fb399c` | 22/10/2026 | Plan de implementación de las respuestas del 22/10/2026 | Consolidado v3 |
| `0dc833a` | 22/10/2026 | El aviso de serie corta nombra la longitud mínima recomendable | Mann-Kendall con n = 7 |
| `1914cec` | 22/10/2026 | Registro de las respuestas y revisión de la DECISIÓN 011 | Partición de Cramer y el resto del consolidado |
| `2e1f1ef` | 29/10/2026 | La Generalizada de Pareto sale del cálculo de la v1 | IV-153 y convenciones de signo |
| `cda6cd3` | 29/10/2026 | Registro de las respuestas del 29/10/2026 y DECISIÓN 084 | Q16, t de Student con n impar |
| `b330f96` | 03/11/2026 | Barrido de las menciones a 13 distribuciones | Salida de la Generalizada de Pareto |

Las respuestas a las preguntas de agregación temporal las implementó también Kevin Massholder (`9376259` y
`bd3dd41`), sobre preguntas propias.

## 5. Fuentes fuera del repositorio

En la carpeta de trabajo del proyecto, fuera de git:

- `Libro/METIS - Informe Final de Grado 09-11-2026.docx`: el informe final. La sección "Distribución del trabajo"
  describe las etapas de cada integrante y resume la autoría con `git blame` al 23/10/2026 (Tabla 24). El Anexo A
  es el registro de decisiones técnicas.
- `Hallazgos - Pendientes/plan-reparto-octavio-kevin.md.docx`: reparto de pendientes acordado tras el relevamiento
  del 02/09/2026. A Octavio Carpineti le asigna el backend pendiente, la fórmula IV-153, la autenticación local, la
  regresión contra la tesis y el seguimiento con Facundo y Carlos ("mandar el documento y hacer seguimiento si no hay
  novedades"). A Kevin Massholder, el cliente web, la gobernanza y la infraestructura, y la corrección de la
  documentación.
- `Hallazgos - Pendientes/METIS_Consolidado_Pendientes_Facundo_Carlos_v3.docx`: el consolidado del 09/09/2026,
  redactado por Octavio Carpineti.
- `Claude Project/Auditoria/Fases/`: las fases de la auditoría. La fase 1 registra verificaciones de Octavio
  Carpineti contra el texto de la tesis, entre ellas la de Cramer y el hallazgo del estadístico tipificado de
  Kolmogorov-Smirnov (Ec. A.57), que corrigió el criterio de esa prueba.

Los documentos de requerimientos, de entendimiento teórico y las notas de las reuniones de abril llevan la firma de
los dos integrantes, sin atribución individual.

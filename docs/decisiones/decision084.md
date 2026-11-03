# DECISIÓN 084: con n impar, la t de Student deja el dato del medio en el segundo subgrupo

**Fecha:** 29 de octubre de 2026
**Estado:** Decidida. Sin cambios de código: registra la convención que METIS ya aplicaba y la fija con un test.
**Decide:** Kevin, con la respuesta de Facundo del 29/10/2026 (consulta C2 del
[plan de mejoras post-despliegue](../Plan%20de%20mejoras%20post-despliegue%20UCC%20y%20respuestas%20de%20Facundo.md)).
**Origen:** Q16 de la consolidación de la fase 4 y la sección "Partición de t de Student con n impar" de
`docs/auditoria/pendientes/pendientes-facundo.md`.

### Problema

La t de Student (Ec. III-8) parte la serie en dos mitades. Con n impar, el dato del medio tiene que ir a alguna:
la tesis lo pone en el primer subgrupo (`n1 = ceil(n/2)`), METIS en el segundo
(`core/pipeline/pipeline_etapa1.py`: `n1_t = n_total // 2`, `n2_t = n_total - n1_t`). La tesis no lo dice en el texto;
sale de reconstruir sus resultados. Corriendo METIS con `ceil(n/2)` se reproduce exactamente la t de la tesis en las
cuatro estaciones con n impar (est_03, 05, 07 y 08), y **en est_05 (n = 39) cambia el veredicto individual**: la tesis
rechaza (t = 2,082 > 2,0262) y METIS acepta (t = 1,817, partición 19 + 20). El nivel de homogeneidad de METIS en est_05
es `homogeneidad_ok`; con la convención de la tesis sería `homogeneidad_warning`.

### Respuesta de Facundo (29/10/2026)

Es indistinto: el subgrupo más grande puede ser el primero o el segundo.

### La decisión

Se mantiene la convención de METIS: **con n impar, el dato del medio va al segundo subgrupo** (`n1 = floor(n/2)`,
`n2 = n − n1`). Es una convención de partición, como el redondeo de los bloques de Cramer (revisión del 22/10/2026 de
la DECISIÓN 011), no una fórmula: las dos son válidas y no hay una referencia que prefiera una.

No se cambia a la de la tesis para reproducir est_05: el criterio del proyecto es reproducir la tesis cuando la tesis
es la fuente de una regla, y acá el autor dice que no lo es. Cambiarla movería un veredicto que hoy está registrado en
los análisis guardados sin que ninguna de las dos lecturas sea más correcta.

- **Test:** `tests/unit/casos_dinamicos/test_valores_limite.py::test_t_student_con_n_impar_el_dato_del_medio_va_al_segundo_subgrupo`
  (casos VL-12a–c de `docs/calidad/casos-de-prueba.md`): n = 39 → 19 + 20, n = 40 → 20 + 20, n = 25 → 12 + 13.
- **Documentación:** la diferencia con la tesis en est_05 queda en `formulas-etapa1.md` §5 y en el libro, como
  diferencia de convención y no como error de ninguna de las dos.

### Relación con otras decisiones

- **DECISIÓN 011** — partición de Cramer; mismo tipo de convención, también confirmada como indistinta por Facundo.

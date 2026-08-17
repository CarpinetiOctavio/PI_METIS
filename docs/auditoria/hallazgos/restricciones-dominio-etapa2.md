# Hallazgos de Auditoría — Restricciones de Dominio en Etapa 2

## Qué es este archivo

Segunda pasada de auditoría, posterior al cierre de las cuatro fases originales
(`docs/auditoria/fases/`, cerradas 09-15/07/2026). No es continuación
secuencial de esa metodología — es una auditoría dirigida a un tema puntual:
el comportamiento de METIS frente a valores que rompen el dominio matemático
de una distribución de Etapa 2 (ceros en la serie, x0 vs. mínimo de la serie,
signo de parámetros estimados). Vive en `hallazgos/` en vez de `fases/`,
`pendientes/` o `regresion/` porque no encaja limpio en ninguna — ver
`docs/README.md` para el criterio.

Llevada en paralelo por Octavio con dos asistentes: una sesión de auditoría
dedicada ("Chat") y Claude Code sobre este repo. Cada hallazgo indica quién lo
originó y quién lo verificó de forma independiente — ningún hallazgo entra acá
sin haber sido chequeado contra el código real o el texto de la tesis por la
otra parte, siguiendo la regla del proyecto de no aceptar afirmaciones sin
verificación cruzada.

**Cada entrada va fechada. No se borra ni se reescribe una entrada anterior —
se corrige agregando una nueva, igual que en `pendientes-facundo.md` y en
`decisiones/`.**

---

## 13/08/2026 — Ronda 1: verificación de 8 puntos de dominio (Etapa 2)

Origen: resumen de Chat tras consultar restricciones de ceros/dominio para
Gamma 3p, Log-Normal 3p, Exponencial (x0,β), Generalizada de Pareto y
Generalizada Exponencial. Verificado por Code contra el código real
(`backend/metis/core/etapa2/distributions/`) y contra `fase1-unitarias.md`.

1. **Chow** — confirmado sin cambios. `backend/metis/core/etapa1/outliers.py:17-36`,
   códigos `TEST_NOT_EXECUTED_ZEROS` y `TEST_NOT_EXECUTED_CONDITION`. Regla
   fija en `constraints.md`, no es una pregunta abierta.

2. **Log-Normal 2p y Log-Pearson III** — confirmado sin cambios.
   `lognormal2p.py:18,32`, `logpearson3.py:31,49` — docstring
   `"Confirmado con Facundo"`, `DISABLED_WITH_ZEROS = True`. Mismo patrón en
   `gamma2p.py:54` y `exponencial_beta.py:29`.

3. **Gamma 3p, x0 ≥ min(serie)** — confirmado sin cambios. Guard explícito en
   Momentos (`gamma3p.py:133-136`) y estructural en MV (bounds,
   `gamma3p.py:160`). `fase1-unitarias.md:403-413`, cita exacta:
   *"CERRADO — FIEL A LA TESIS, sin hallazgos de fórmula."*

4. **Gamma 3p, ¿tolera cero en la serie cruda?** — confirmado que SÍ, con
   evidencia de código (no solo de fórmula). `gamma3p.py` no tiene ningún
   `np.any(serie == 0)` — el log solo se aplica a `zi = xi - x0`, nunca a
   `xi` crudo, y `x0` queda forzado por debajo del mínimo por los guards del
   punto 3.

5. **Log-Normal 3p, ¿misma restricción?** — confirmado, mismo patrón exacto
   que Gamma 3p. Guard explícito en Momentos (`lognormal3p.py:159`),
   estructural en MV (bounds, `lognormal3p.py:190`). `fase1-unitarias.md:375-391`,
   cita exacta: *"CERRADO — FIEL A LA TESIS."* Tampoco tiene
   `np.any(serie == 0)` — tolera cero en la serie cruda por la misma razón
   que Gamma 3p.

   **Hallazgo agregado, no estaba en el resumen de Chat:** de las 5
   distribuciones marcadas `PENDING_ZEROS_CONFIRMATION = True`, el
   comportamiento real en código no es uniforme pese a docstrings casi
   idénticos — Gamma 3p y Log-Normal 3p no bloquean cero; Exponencial (x0,β),
   Generalizada de Pareto y Generalizada Exponencial sí lo bloquean
   explícito (`exponencial_x0_beta.py:42-45`, `gen_pareto.py:83-86`,
   `gen_exponencial.py:55-58`).

6. **Generalizada Exponencial, Momentos-L, λ negativo** — confirmado sin
   ningún guard en código (`gen_exponencial.py:197-200`, con comentario ya
   existente citando est_02). La duda de rotulado de estación (NOTA
   10/07/2026 en `pendientes-facundo.md`) fue verificada manualmente por
   Octavio contra la tesis para las 9 estaciones — sin estación cruzada — y
   ya quedó documentada en `pendientes-facundo.md` (actualización 13/08/2026,
   sección "Gen. Exponencial — Método Momentos L").

   Verificado además, de forma independiente, el argumento matemático de
   que λ<0 no admite solución real: con IV-76,
   F(x) = (1−e^(−λ·x))^ε. Para λ<0 y x>0: e^(−λ·x) = e^(|λ|·x) > 1, así que
   (1−e^(−λ·x)) < 0 para todo x>0 — la base de la potencia es negativa,
   F(x) queda indefinida (o negativa) en todo el dominio x>0, no en un punto
   aislado. Confirma la afirmación con una derivación real.

7. **Exponencial x0-β y Generalizada de Pareto** — confirmado, genuinamente
   abiertas. Verificado directo contra el PDF de la tesis
   (`Analisis Frecuencia - IV-56 a 120.pdf` pág. 65-66,
   `IV-121 a 199.pdf` pág. 73 — fuera del repo, en
   `/Users/octavio/Desktop/Auditoria Etapa 2/`): ni IV-68/69 ni IV-145/146
   tienen una cláusula equivalente a IV-65
   ("esta función es válida para: x > 0"). `fase1-unitarias.md:350-355` y
   `:418-427` las cierran solo en fidelidad de fórmula. Pregunta de dominio
   ante ceros sigue agrupada en `pendientes-facundo.md`, sección "Etapa 2 —
   comportamiento ante ceros de 5 distribuciones".

8. **Gamma 3p MPP, ausente del Capítulo IV** — ya documentado, con más
   contexto del que tenía Chat. Ya trackeado en
   `.claude/rules/core/formulas-etapa2.md` (sección "Pendientes", ítems 1-2)
   y `docs/auditoria/regresion/README.md` ("Exclusiones globales"). No hay
   ninguna fórmula MPP implementada en `gamma3p.py`
   (`METODOS_APLICABLES = ("momentos", "mv")`, sin `"mpp"`) — el método está
   simplemente excluido, no hay fórmula de ningún origen que verificar.
   Dato adicional no mencionado por Chat: `fase1-unitarias.md:338-342` ya
   registra una hipótesis no confirmada de por qué — *"el método de
   Greenwood et al. (1979), citado como origen del MPP, es explícitamente
   para distribuciones expresables en forma inversa — Gamma no lo es."*

---

## 13/08/2026 — Hallazgo: guard de dominio faltante en Exponencial x0-β, Momentos

**Estado (13/08/2026): hallazgo verificado, sin aplicar — pendiente de fix
en código, no pendiente de pregunta a Facundo. Actualizado 17/08/2026 —
APLICADO, ver [DECISIÓN 060](../../decisiones/decision060.md) y la entrada
de esa fecha más abajo en este mismo archivo.**

### El hallazgo

`exponencial_x0_beta.py::ajustar("momentos")` no verifica `x0 < min(serie)`,
a diferencia de Gamma 3p y Log-Normal 3p (punto 3 y 5 de arriba), que sí lo
hacen. La restricción de soporte de la distribución (IV-68/69: x > x0) es la
misma en las tres — Momentos y MV comparten la restricción de fondo, no es
casualidad que las tres tengan la misma forma matemática (`x > x0`
equivalente a `x0 < min(serie)`).

MV sí la garantiza por construcción: `x1 = min(serie)`, `beta` se rechaza si
`≤0` (`exponencial_x0_beta.py:72`), y `x0 = x1 - beta/n` con `beta>0` da
necesariamente `x0 < x1`. Momentos no: `x0 = xbar - S` (IV-71), sin ningún
chequeo posterior.

**Verificado con smoke test, sin ningún cero en la serie:**
```
serie = [10, 11, 12, 13, 14]
Momentos → x0 = 10.4189, min(serie) = 10.0   → x0 >= min(serie): True, status=ok (sin marcar)
MV       → x0 = 9.5,      min(serie) = 10.0  → x0 >= min(serie): False, correcto
```

**Ya ocurre en el dataset real de la tesis, sin que ninguna auditoría previa
lo haya marcado:** est_04 (Las Tapias), `Exponencial x0β Momentos` —
`docs/auditoria/regresion/regresion-e2e-coreEstadistico/est_04-e2e.md:92` —
x0 METIS=4.3279, x0 tesis=4.33, ambos por encima del `min(serie)=2.0` de esa
estación. La fila está marcada `~0%` — PASS — porque `fase1-unitarias.md:350-355`
(§3.3) cerró esa sección solo en fidelidad de fórmula, sin evaluar la
restricción de dominio.

**Dato relevante para el encuadre:** en Gamma 3p, cuando la tesis tiene
x0>min(serie), lo marca (EEA=NO_APLICABLE, ver `pendientes-facundo.md`,
sección "Gamma 3p — parámetros calculados con x0 > min(serie)"). En est_04,
la tesis reporta un EEA completo y limpio (4.7691) pese a la misma
violación — la tesis no trata esta restricción igual en las dos
distribuciones. Esto no invalida que la restricción matemática exista (el
soporte de IV-68/69 sigue exigiendo x>x0) — solo que no hay, acá, evidencia
empírica de la fuente primaria aplicándola de la misma forma que en Gamma 3p.

### Hipótesis sobre por qué el Excel de Facundo no lo detectó — marcada como conjetura, no como hecho

Chat propuso una explicación estructural: en Gamma 3p, `(x-x0)^(β-1)` con
exponente no entero y base negativa no tiene solución real en una fórmula de
celda de Excel (`#¡NUM!`) — Facundo lo habría visto como error. En
Exponencial x0-β, `e^(-(x-x0)/β)` está definida para cualquier valor real,
incluso con `x-x0` negativo — el cálculo no falla, solo produce un número
fuera del soporte declarado por la fórmula, sin ningún aviso.

**Esto es plausible pero no verificado — no se trata como hecho.** El propio
`pendientes-facundo.md` marca reiteradamente ("Causa C") que el
funcionamiento interno del Excel de Facundo no es verificable sin acceso al
archivo real. Hay además un matiz que complica la historia limpia: el
cuantil de Gamma 3p que efectivamente entra en el cálculo de EEA (IV-144,
Wilson-Hilferty) es una aproximación cerrada que no evalúa
`(xi-x0)^(β-1)` sobre datos crudos en ningún punto del pipeline documentado
— si Facundo siguió el mismo camino (IV-144, no la densidad cruda), el
"error ruidoso" de la hipótesis no tendría dónde dispararse tampoco en
Gamma 3p. Sin el archivo de Facundo, no se puede cerrar esto en ninguna
dirección.

### Por qué no es una pregunta para Facundo

La restricción de soporte (x > x0) está explícita en la propia fórmula de la
tesis (IV-68/69) — no es una ambigüedad de intención como "¿tolera cero?"
(punto 4/5 de la ronda de arriba), donde hay más de una resolución
razonable pendiente del juicio de dominio de Facundo. Acá no hay
alternativa matemática válida: si `x0 ≥ min(serie)`, el modelo ajustado
implica que la serie tiene datos por debajo del soporte que el propio
modelo declara. Precedente directo en el proyecto: DECISIÓN020, DECISIÓN023
y DECISIÓN025 ya agregaron guards de dominio por exigencia matemática de la
fórmula, sin escalar a Facundo — mismo tipo de cambio.

**Acción pendiente (no aplicada):** agregar a `exponencial_x0_beta.py::ajustar("momentos")`
un guard `if x0 >= min(serie): STATUS_NO_APLICABLE`, simétrico al que ya
tienen Gamma 3p y Log-Normal 3p. Cuando se aplique, este hallazgo pasa a
decisión numerada (`decisiones/decisionNNN.md`), siguiendo el mismo patrón
que DECISIÓN023/025.

---

## 17/08/2026 — Corrección: censo subestimado, y hallazgo nuevo en Generalizada de Pareto

**Corrección sobre la entrada del 13/08/2026 de arriba — no se borra, se
corrige acá.** La entrada original decía "ya ocurre en el dataset real... un
caso: est_04". Es una subestimación — se corrió `exponencial_x0_beta.py::ajustar("momentos")`
contra las 9 series reales de la tesis (no solo est_04), extraídas
directamente de `docs/auditoria/regresion/regresion-unitaria/est_0X-*.md`.

### Exponencial (x0, β), Momentos — censo completo de las 9 estaciones

| Estación | min(serie) | x0 (Momentos) | ¿Viola x0≥min? |
|---|---|---|---|
| est_01 (Alpa Corral) | 15.0 | 28.60 | **Sí** |
| est_02 (Vado de Río Seco) | 42.0 | 33.87 | No |
| est_03 (La Tapa) | 2.0 | -14.83 | No |
| est_04 (Las Tapias, R. Las Tapias) | 2.0 | 4.33 | **Sí** |
| est_05 (Piedra Blanca) | 0.9 | -1.35 | No |
| est_06 (Las Tapias, R. San Bartolomé) | 14.0 | 16.34 | **Sí** |
| est_07 (Tincunaco) | 11.8 | 24.34 | **Sí** |
| est_08 (Ume Pay) | 39.2 | 68.48 | **Sí** |
| est_09 (La Suela) | 10.99 | 18.22 | **Sí** |

**6 de 9 estaciones violan, no 1.** El módulo devuelve `STATUS_OK` en los 9
casos — nunca detecta la violación en ninguno. Reproducible con
`backend/metis/core/etapa2/distributions/exponencial_x0_beta.py::ajustar`,
llamado directo sobre cada serie de `regresion-unitaria/`.

### Generalizada de Pareto, Momentos — hallazgo nuevo, mismo patrón exacto

`gen_pareto.py::ajustar("momentos")` tiene la misma estructura: `mu = xbar - sigma/(1+eps)`
(IV-147 despejado), sin ningún chequeo posterior contra `min(serie)` — mismo
hueco que Exponencial x0-β, misma restricción de fondo (soporte x≥µ de
IV-145/146).

| Estación | min(serie) | µ Momentos | ¿Viola? | µ MV | µ MC | µ MPP |
|---|---|---|---|---|---|---|
| est_01 | 15.0 | -7.70 | No | NO_CONVERGE | 15.00 (≈min, no viola) | -33.20 |
| est_02 | 42.0 | 27.13 | No | NO_CONVERGE | NO_CONVERGE | -22.16 |
| est_03 | 2.0 | -3.41 | No | NO_CONVERGE | 2.00 (≈min) | -20.25 |
| est_04 | 2.0 | **4.09** | **Sí** | NO_CONVERGE | NO_CONVERGE | -6.98 |
| est_05 | 0.9 | -2.05 | No | NO_CONVERGE | NO_CONVERGE | -16.01 |
| est_06 | 14.0 | 10.95 | No | NO_CONVERGE | 14.00 (≈min) | 2.16 |
| est_07 | 11.8 | **16.98** | **Sí** | NO_CONVERGE | 11.80 (≈min) | -19.84 |
| est_08 | 39.2 | **45.70** | **Sí** | NO_CONVERGE | 39.20 (≈min) | -0.33 |
| est_09 | 10.99 | 3.61 | No | NO_CONVERGE | 10.96 | -34.24 |

**Momentos: 3 de 9 violan (est_04, est_07, est_08).** MV, MC y MPP: **sin
violaciones en ninguna de las 9** — verificado, no solo asumido:

- **MV** fija `mu = min(serie)` por construcción antes de resolver ε y σ
  (`gen_pareto.py:133`) — siempre válido para el soporte inclusivo de GPD
  (x≥µ). No converge en ninguna de las 9 series reales (consistente con
  `formulas-etapa2.md`: *"NOTA: MV y MC frecuentemente No Converge según
  resultados de la tesis"*), pero la seguridad es por diseño, no por
  casualidad del dataset.
- **MPP** da `mu = x1 - sigma/(n+eps)` (IV-169) — mismo mecanismo
  estructural que el MPP de Gamma 3p: con σ>0, siempre queda por debajo del
  mínimo salvo que `n+ε` sea negativo (no ocurrió en ninguna de las 9).
- **MC** converge al mínimo casi exacto en varios casos (fenómeno de borde
  cuando ε→0) pero nunca lo supera en las 9 series.

### Guards faltantes — actualización de la acción pendiente

Reemplaza la acción pendiente de la entrada del 13/08/2026: son **dos**
archivos con el mismo hueco, no uno.

```python
# exponencial_x0_beta.py, rama "momentos", después de x0 = xbar - S:
if x0 >= float(np.min(serie)):
    return MetodoResult(metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE)

# gen_pareto.py, rama "momentos", después de mu = xbar - sigma / (1.0 + eps):
if mu >= float(np.min(serie)):
    return MetodoResult(metodo=metodo, parametros=None, eea=None, status=STATUS_NO_APLICABLE)
```

Mismo patrón que `gamma3p.py:133-136` y `lognormal3p.py:159`. Generalizada
Exponencial no aplica — no tiene parámetro de posición (solo α, λ), es otra
categoría de problema.

**APLICADO — 17/08/2026, mismo día.** Ver [DECISIÓN 060](../../decisiones/decision060.md)
para el detalle completo de la aplicación y la verificación contra las 9
estaciones post-fix. Los dos guards de arriba fueron agregados tal como se
proponían, sin cambios de diseño respecto a lo documentado acá. Este
hallazgo queda cerrado — de acá en más, `DECISIÓN 060` es la fuente de
verdad sobre el estado del código; este archivo conserva el razonamiento
de cómo se encontró.

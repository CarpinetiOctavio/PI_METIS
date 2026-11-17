# Auditoría de las fórmulas del modo paso a paso (LaTeX) — 20/09/2026

**Alcance:** las 8 pruebas de Etapa 1 con fórmula en `frontend/src/i18n/explicaciones.ts`
(`FORMULAS_LATEX`, y el texto plano de respaldo). **Solo lectura**: no se modificó ningún archivo
de `backend/` ni de `frontend/`. Los cambios que salgan de acá esperan confirmación (ver
"Estado").

**Fuentes contrastadas:**

| Prueba | Fuente primaria | Cómo se verificó |
|---|---|---|
| Anderson, Wald-Wolfowitz, Helmert, t de Student, Cramer | Tesis de Facundo, cap. III (pp. 46–51) | Páginas renderizadas y leídas como imagen (el texto extraído del PDF sale garbleado en las ecuaciones) |
| Mann-Kendall, Kolmogorov-Smirnov | Caamaño & Dasso, *Lluvias de Diseño*, Apéndice A.5 (pp. 204–206) | Ídem, ecuaciones A.51–A.57 y Tablas A.4/A.5 |
| Chow | Bulletin 17B, Apéndice 4 (DECISIÓN 018) | **No está en el repo** — solo se pudo verificar contra el código y numéricamente |

## 1. Matriz

`=` coincide · `≠` difiere · `+` falta un paso en la pantalla

| Prueba | LaTeX mostrado | `formulas-etapa1.md` | Código (`core/etapa1/`) | Fuente |
|---|---|---|---|---|
| **Anderson** | r_k (III-1), sustitución y resultado | **≠** (§2 dice `n//3` y `lags_fuera/k_max ≤ 0.10`) | `=` a la tesis (`ceil(n/3)`, `ceil(0.1·k_max)`: DECISIONES 016/012) | III-1 `=`. **+** III-3 (bandas) y la regla del 10% no se muestran |
| **Wald-Wolfowitz** | Z = (R−μ_R)/σ_R | `=` | `=` (σ_R algebraicamente idéntica a III-6) | III-4 impresa con σ²_R: errata de la tesis, la pantalla usa σ_R (correcto). **+** III-5 y III-6 no se muestran |
| **Helmert** | S−C contra √(n−1) | `=` | `=` | III-7 `=` |
| **t de Student** | t = Δx̄ / (S_p·√(1/n₁+1/n₂)) | `=` | `=` (`sp2 = (n1·var1 + n2·var2)/ν`, `ddof=1`) | III-8 `=` en valor. **+** S_p nunca se define |
| **Cramer** | t_w (III-15), bloques 60% / 30% | `=` | `=` | III-15 `=`. **+** τ_w (III-13/14) y S_Q (III-10) no se muestran. **≠** rótulos 60%/30% fijos |
| **Mann-Kendall** | S, Var(S), Z en prosa | `=` | Z de `pymannkendall` (con corrección por empates) | A.55 `=` sin empates. **≠** valor crítico: 1,96 vs. 1,64 de la Tabla A.4 |
| **Kolmogorov-Smirnov** | Z = D·√(n₁n₂/(n₁+n₂)) | `=` | `=` | A.57 `=`, Tabla A.5 (1,358) `=`. **+** D (A.56) no se define |
| **Chow** | K_N y t_Bonferroni | `=` | `=` | Bulletin 17B: **no verificable localmente**; ver H-6 |

## 2. Hallazgos

Clasificados por dónde hay que corregir. **Ninguno está aplicado.**

### A. Discrepancias de contenido — requieren tu confirmación

**H-1 — Cramer: los rótulos "Bloque 60%" y "Bloque 30%" son texto fijo** (`explicaciones.ts:72-73,
211-216, 306`). Con una partición personalizada (DECISIÓN 036, cerrada el 18/08/2026) el usuario
elige otros porcentajes y la pantalla sigue diciendo 60/30. `terminos` no lleva los porcentajes
(`homogeneity.py:209-221`), así que el frontend no puede corregirlo solo.
*Corrección:* `n1_pct`/`n2_pct` en `terminos` (**toca backend**, aditivo) y usarlos en los rótulos.

**H-2 — Mann-Kendall: el valor crítico difiere de la fuente citada.** La Tabla A.4 del apéndice
(la que cita `formulas-etapa1.md`) da `V_crít = 1,64` para α = 0,05. METIS usa 1,96 (normal
bilateral, `trend.py:9`). No es un error de cuenta: 1,64 es el cuantil de una cola y 1,96 el de dos
colas, y `pymannkendall` decide con dos colas. Pero `formulas-etapa1.md` §7 lo presenta como
consistente con la fuente y un alumno que abra el libro va a ver 1,64. Además la prosa de la
pantalla dice "corrección por empates, Kendall 1975" y A.55 **no** tiene corrección por empates
(solo el `I−1` de continuidad); esa corrección es de la librería.
*Decisión a tomar:* ¿se mantiene 1,96 y se documenta la divergencia con la Tabla A.4, o se
alinea con la fuente? Es una pregunta de dominio (Facundo/Carlos).

**H-3 — t de Student: S_p aparece sin definición.** La tesis (III-8) no usa el símbolo S_p: pone
el radical entero. La pantalla lo introduce en el paso 1 pero no muestra
`S_p² = (n₁s₁² + n₂s₂²)/(n₁+n₂−2)`, y el denominador del paso 2 lo arma el frontend
(`sp·√(1/n1+1/n2)`, `explicaciones.ts:182`). Dos matices: (a) la tesis no dice si `s²` es sesgada
o insesgada; el código usa `ddof=1` multiplicado por `n` (confirmado con est_02, DECISIÓN
documentada en `formulas-etapa1.md` §5), que **no** es el estimador combinado de los libros de
texto; (b) esa reconstrucción en el frontend roza la regla de DECISIÓN 064 ("el frontend no
recalcula").
*Corrección:* mostrar la definición de S_p²; el denominador podría viajar en `terminos`
(**toca backend**, aditivo).

**H-6 — Chow: el valor crítico difiere de la tabla de Bulletin 17B, y la pantalla no dice qué α se usa.**
El código usa α = 0,10 (`outliers.py:10`) con `t_{ν, 1−α/(2n)}`: un test **bilateral** al 10%. Los
valores resultantes son 2,176 (n=10), 2,557 (n=20), 2,745 (n=30), 2,868 (n=40), 2,957 (n=50).
Si en cambio se usa una cola, `t_{ν, 1−α/n}` con el mismo α = 0,10, se obtienen 2,036, 2,385,
2,565, 2,684, 2,772. **Recuerdo** que la tabla de K_N del Apéndice 4 del Bulletin 17B trae
2,036 (n=10), 2,385 (n=20), 2,563 (n=30), 2,682 (n=40) y 2,768 (n=50): coinciden con la variante
de una cola hasta el tercer decimal en n=10 y n=20. `formulas-etapa1.md` §9 afirma que K_N=2,745 para
n=30 "coincide con el valor citado para la tabla del Apéndice 4", y eso choca con esa tabla.
**Esto es de memoria y el Bulletin no está en el repo: hay que verificarlo contra el original antes
de tocar nada.** Si se confirma, el criterio actual es más conservador que el del Bulletin (la
diferencia es de ≈7% en K_N para n entre 10 y 50) y **cambia qué series disparan la pausa de atípico**. Por eso no
es una corrección del modo educativo sino un hallazgo del `core/` para una decisión aparte
(complementa DECISIÓN 018, cuyo addendum dice que Carlos confirmó la fuente pero no qué variante
del cuantil).
Independiente de lo anterior, la pantalla escribe `t_{n−2, 1−α/(2n)}` sin decir que aquí
α = 0,10 y no el 0,05 del resto de Etapa 1: el alumno no puede reproducir `t_Bonferroni`.
*Corrección de pantalla:* rotular α = 0,10 (solo frontend).
**Decisión (Kevin, 20/09/2026): el valor crítico de Chow se deja como está** (Octavio
probablemente ya lo controló). No se toca `outliers.py` ni se abre decisión; solo se corrige el
rótulo de α en la pantalla.

### B. Pasos que faltan en la pantalla — corrección solo de frontend salvo lo indicado

**H-4 — Anderson:** no se muestra III-3 (las bandas por lag, que son la mitad de la prueba) ni la
regla del 10%; solo III-1 para el lag de mayor |r_k|. Es el objetivo de los ítems E y F del plan
(el desglose por lag necesita datos nuevos: **toca backend**).

**H-5 — Wald-Wolfowitz:** μ_R y σ_R aparecen como números, sin sus fórmulas III-5 y III-6.
`terminos` ya trae `n1`, `n2`, `n`: alcanza con frontend.

**H-7 — Cramer:** τ_w (III-13/14) y S_Q (III-10) aparecen como números sin fórmula. `terminos` ya
trae `media_global`, `s_global`, `tau_w1`, `tau_w2`: alcanza con frontend.

**H-8 — Kolmogorov-Smirnov:** D se muestra sin definirlo (A.56). Alcanza con frontend.

**H-9 — Mann-Kendall:** Var(S) se muestra como número, sin fórmula. Con la corrección de
empates de la librería, la fórmula literal de A.55 solo vale sin empates
(`N(N−1)(2N+5)/18`). Mostrarla exige aclarar eso; se puede hacer solo con frontend.

### C. Documentación desactualizada — `.claude/rules/`

**H-10 — `formulas-etapa1.md` §2 (Anderson)** dice `k_max = n // 3` y
`aprobada = (lags_fuera / k_max) ≤ 0.10`. El código usa `k_max = ceil(n/3)` (DECISIÓN 016) y
`lags_fuera ≤ ceil(0.10·k_max)` (DECISIÓN 012). Con k_max = 9 el documento no tolera ningún lag
fuera y el código tolera uno. El código está respaldado por decisiones; el documento que "se lee
siempre" está mal. `statistical-pipeline.md` repite el `n/3`.

### D. Verificado sin diferencias

- **Anderson III-1**, **Helmert III-7**, **Cramer III-15**, **KS A.57 y Tabla A.5** coinciden
  exactamente entre pantalla, código y fuente.
- **Wald-Wolfowitz:** `σ_R = √[2n₁n₂(2n₁n₂−n₁−n₂)/(n²(n−1))]` del código es algebraicamente idéntica
  a III-6 (`(μ_R−1)(μ_R−2)/(n−1)` con n = n₁+n₂). Difiere solo cuando hay valores iguales a la
  media, que el código excluye (DECISIÓN 017).
- **Cramer, ν:** la tesis escribe `ν = n₁+n₂−2` y el código usa `ν = n−2` (DECISIÓN 011, pendiente
  de confirmación formal con Facundo). La pantalla no muestra ν, así que no hay nada que corregir
  ahí.
- **Anderson, límites de k:** la tesis dice `k = 1..n/3` sin redondear; el código `ceil(n/3)`
  (DECISIÓN 016).

## 3. Qué requiere backend (para dejar al final, con Octavio)

| Hallazgo | Toca backend | Para qué |
|---|---|---|
| H-1 | Sí, aditivo | `n1_pct`/`n2_pct` en `terminos` de Cramer |
| H-3 | Opcional, aditivo | Denominador de t en `terminos` (sacarlo del frontend) |
| H-4 (E/F) | Sí, aditivo | `desglose` por lag en Anderson |
| H-6 (valor crítico) | **Sin acción** | Decisión de Kevin: se deja como está. Solo cambia el rótulo de α (frontend) |
| H-2 | Solo si se decide alinear con la Tabla A.4 | Decisión de dominio |
| H-5, H-7, H-8, H-9, rótulo de α en H-6 | No | Solo `explicaciones.ts` |
| H-10 | No | Solo `.claude/rules/` |

## 4. Estado

Confirmado por Kevin el 20/09/2026. Ningún hallazgo está aplicado todavía. Reparto acordado, en
`docs/plan-feedback-directores-20-09-2026.md` §5 ("Resultado y reparto de los hallazgos"):

- **Fase D2 (sin backend, PR propio):** H-2 (solo prosa y documentación), H-3 (definición de S_p),
  H-5, H-7, H-8, H-9, H-10, H-1 (rótulos interinos por n_w) y el rótulo de α de H-6.
- **Fase E, Tanda 2 (backend, tras consultar con Octavio):** bandas por lag de Anderson (H-4),
  `n1_pct`/`n2_pct` de Cramer (H-1 definitivo) y el denominador de t (H-3 restante).
- **Sin acción:** el valor crítico de Chow (H-6, decisión de Kevin) y el de Mann-Kendall (H-2,
  a la espera de la pregunta 7 del plan, §1).

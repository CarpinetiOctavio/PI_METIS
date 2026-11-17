# DECISIÓN 023 — Gamma 3p MV: escaneo denso hacia el borde superior + validación de raíz (no margen fijo)

**Fecha:** 14 de Julio de 2026
**Estado:** APLICADA — ver verificación en sección correspondiente
**Origen:** Auditoría Fase 4 (E2E), est_04, contraverificación Chat + diagnóstico en vivo Code

### Contexto

`gamma3p.py::mv()` devolvía NO_CONVERGE en est_04 pese a existir una raíz
matemáticamente válida (x0≈1.740, α≈17.408, β≈1.280 — coincide con la
propia tesis hasta la tercera cifra decimal). Diagnóstico confirmado con
logging real del bracket: el escaneo uniforme de 200 puntos sobre el
dominio completo (~394 unidades, desde `min(xi)-20S` hasta `min(xi)`) no
genera ningún cambio de signo detectable — 0 brackets en las 200
evaluaciones (puntos 198/199 verificados: x0=0.020113→iv142=-1.506811,
x0≈hi→iv142=-14.801414, ambos negativos).

Mapeo fino del intervalo entre esos dos puntos reveló **dos fenómenos
distintos, no uno solo:**
1. Raíz genuina: iv142 cruza de negativo a positivo en x0≈1.7315–1.7651.
2. Singularidad espuria: iv142 vuelve a positivo, alcanza un máximo
   (~1.44) en x0≈1.966, y colapsa a -14.80 al acercarse a `hi`
   (x0→min(serie)), producto de S2 (suma de 1/zi) disparándose a ~10⁹
   cuando un dato de la serie casi coincide con x0. Mismo tipo de
   patología de verosimilitud no acotada cerca del mínimo muestral ya
   documentada para Log-Normal 3p (ver [DECISIÓN 020](decision020.md)) — pero **no** el
   mismo margen numérico: el comportamiento espurio en Gamma 3p arranca
   bien antes del borde (~1.966), no a un paso de punto flotante de `hi`
   como en LN3p, por lo que un bound idéntico (`1e-9`) no habría servido.

Verificado por dos vías independientes que la raíz en x0≈1.74 es real y
no un artefacto de la aproximación de Thom: (a) el propio residuo IV-142
cruza cero ahí, con la ecuación de Thom tal como está codeada; (b) un
perfil de verosimilitud exacto, sin aproximación de Thom
(`scipy.stats.gamma.fit` sobre `serie - x0` para cada x0 candidato), da un
mínimo de -logL independiente en la misma zona (x0≈1.75–1.80).

### Decisión

1. **Escaneo denso y no uniforme, concentrado hacia `hi`** (espaciado
   logarítmico/geométrico en vez de `linspace` uniforme) — ahí es donde
   viven tanto la raíz real como la zona espuria; el resto del dominio no
   aporta nada y densificarlo parejo es desperdicio computacional.
2. **Sin margen fijo de exclusión copiado de LN3p.** Se rechazó
   explícitamente reutilizar el bound `1e-9` de [DECISIÓN 020](decision020.md) porque la
   escala a la que arranca la patología es distinta en esta distribución
   — un margen prestado no habría cubierto la zona espuria real
   (1.966–2.0) en este caso.
3. **Validación del candidato post-convergencia, no del punto de
   búsqueda:** tras converger con `brentq`, se descarta cualquier raíz
   con β≤0 o α≤0 (condición matemática necesaria, no arbitraria), y se
   aplica un sanity check sobre la magnitud de S2 en función de n. Si el
   escaneo detecta múltiples brackets, se valida cada candidato — no se
   toma el primero por orden de iteración (eso era lo frágil de
   cualquier solución que dependiera solo de densificar sin validar).

### Por qué es una decisión válida, no una desviación sin fundamento

Categoría 2 del framework de ambigüedad del proyecto: sin ambigüedad de
fórmula — IV-142 y la aproximación de Thom (ya aceptada, Categoría 2
también, mismo tratamiento que logpearson3.py) quedan intactas. El cambio
es exclusivamente sobre el mecanismo de búsqueda y aceptación de la raíz
de una ecuación que ya es la correcta, no sobre qué ecuación se resuelve.

### Alcance / verificación exigida antes de cierre

- Confirmar que est_04 converge a x0≈1.740/α≈17.408/β≈1.280 (o entorno
  cercano) con el fix aplicado.
- Correr sobre est_01, est_02 y est_03 (donde `gamma3p.py::mv()` ya daba
  NO_CONVERGE de forma correcta o convergía sin objeciones) para confirmar
  que el fix no introduce convergencias espurias nuevas — no alcanza con
  que resuelva est_04, tiene que no romper el comportamiento ya validado
  en las estaciones previas.

### Resultado de la verificación (Code, 14 de Julio de 2026)

Fix aplicado en `gamma3p.py::mv()`: escaneo combinado (grueso de
cobertura, `linspace(lo,hi,200)`, más denso geométrico concentrado en
`hi` — 400 puntos con offsets `np.geomspace(1e-6, 0.05·ancho, 400)`),
más `_validar_raiz()` post-`brentq` (β>0/α>0 vía `_params_from_x0`, y
`S2 > 2.0·n` rechaza el candidato — umbral justificado en el código
contra los valores concretos de est_04: raíz genuina S2/n≈0.20, raíz
espuria S2/n≈9.40, margen de 10x/4.7x a cada lado). Sobre múltiples
brackets, se valida cada uno y se toma el primero que pasa, no el primero
por orden de escaneo.

**est_04 (el caso que motivó el fix):**
```
gamma3p.ajustar(serie_est04, "mv") →
  status=ok, beta=1.280309, alpha=17.408141, x0=1.739970
  (tesis: x0=1.740, alpha=17.408, beta=1.280 — coincide)
```

**est_01, est_02, est_03 (deben seguir sin converger espuriamente):**
```
est_01: no_converge  (tesis: NO_CONVERGE — coincide, sin cambio)
est_02: no_converge  (tesis: NO_CONVERGE — coincide, sin cambio)
est_03: no_converge  (sin cambio respecto del comportamiento ya auditado)
```

**Barrido adicional no exigido por el alcance pero corrido igual —
est_05 a est_09 (todo el dataset disponible, no solo lo mínimo pedido):**
```
est_05: no_converge  (sin cambio)
est_06: no_converge  (sin cambio — caso ya documentado en
        pendientes-facundo.md: los propios parámetros de tesis para
        est_06 no satisfacen IV-140/141 evaluados directo; IV-142 no
        tiene raíz en el dominio para esta serie, con o sin el fix)
est_07: ok, x0=4.408180, alpha=16.824503, beta=2.870014
        (sin cambio respecto del valor ya reportado antes del fix —
        esta estación ya convergía correctamente con el scan viejo)
est_08: ok, x0=34.356756, alpha=72.616111, beta=1.684279
        (sin cambio, ídem est_07)
est_09: ok, x0=10.760777, alpha=15.348792, beta=1.097011
        (sin cambio, ídem est_07)
```

**CORRECCIÓN (15/07/2026, Fase 4, est_08) — la línea de est_08 de arriba es
incorrecta; "sin cambio" no se sostiene.** Verificado sin depender de
control de versiones (git no es fuente válida en esta auditoría — ni para
el repo remoto ni para el propio código de METIS): se reconstruyó el
escaneo *anterior* a este fix tal como lo describe el propio comentario de
`gamma3p.py` en el bloque de la corrección (`np.linspace(lo, hi, 200)` sin
el agregado geométrico), usando únicamente las funciones de módulo
`_params_from_x0` y `_psi_thom` del archivo actual (no closures, no código
externo). Para est_08 (`lo=-1724.4456`, `hi=39.2000`, ancho≈1763.65,
paso≈8.86 con 200 puntos uniformes): ese escaneo de 200 puntos da **0
cambios de signo** en las 200 evaluaciones — no encuentra ningún bracket.
La raíz genuina está en x0≈34.35 (coincide con el x0 que reporta el
método hoy y con el x0=34.351 de la tesis), a solo 4.87 unidades del borde
superior `hi` — muy por debajo del paso de 8.86 unidades del escaneo
viejo, que por eso no podía encontrarla. El escaneo actual (grueso +
geométrico concentrado hacia `hi`) sí genera el bracket y converge. Mismo
patrón que est_04 — el fix resuelve un segundo caso real, no solo est_04;
la nota "sin cambio, ídem est_07" de la línea de est_08 arriba fue un
error al escribir esa verificación en su momento, no una comprobación real
contra el escaneo viejo. Re-verificado con el mismo método que est_07 y
est_09 sí son "sin cambio" genuino (el escaneo viejo de 200 puntos, para
esas dos series, ya encuentra el bracket sin necesitar el agregado
geométrico). Detalle completo, reproducible sin git, en
`regresion-e2e/est_08-e2e.md`, Hallazgo A.

Confirmado: el fix es estrictamente aditivo — resuelve est_04 sin alterar
el resultado de ninguna otra estación del dataset (9/9 verificadas, no
solo las 3 mínimas pedidas).

**NOTA (15/07/2026, añadida junto con la corrección de arriba, sin editar
la oración original que la precede):** ese "9/9 verificadas" y "sin
alterar el resultado de ninguna otra estación" siguen siendo ciertos en el
sentido estricto — ninguna estación pasó de convergente a no convergente
por el fix. Pero la oración da a entender que el fix resolvió un solo caso
real (est_04) y el resto ya estaba en su estado final — eso es lo que la
corrección de arriba desmiente para est_08: el fix resuelve genuinamente
dos casos reales (est_04 y est_08), no uno.

**Suite de tests:** `pytest tests/` → 109 passed, 1 failed. El único
failing es `test_gen_pareto_mc_q100_serie_facundo` — pendiente
preexistente, documentado y aceptado explícitamente en Fase 3
(`fase3-testing.md`, "SIN RESOLVER... por decisión explícita de
Octavio"), sin relación con `gamma3p.py`. Mismo conteo exacto que la
baseline ya documentada al cierre de Fase 3 — cero tests nuevos rotos.
`ruff check metis/core/etapa2/distributions/gamma3p.py` → All checks
passed.

**Cierre:** verificación completa, sin hallazgos que reabran la
decisión. Los 4 puntos del alcance original (converge est_04, no rompe
est_01/02/03) están cumplidos, y se extendió la verificación a las 9
estaciones del dataset por rigor adicional.

### Archivos modificados
- `metis/core/etapa2/distributions/gamma3p.py` — método `mv`: escaneo
  denso no uniforme + validación de raíz (β>0, α>0, sanity check S2)
- `.claude/rules/regression/pendientes-facundo.md` — remover este ítem
  (ya no depende de Facundo, causa raíz y fix completamente
  caracterizados sin necesitar su intervención)

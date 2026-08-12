# Estrategia de Testing — METIS

## Cuatro niveles obligatorios (comprometidos en el anteproyecto)

**Estado real, no solo compromiso (verificado 09/08/2026, actualizado en el
cierre del Bloque A del plan de Etapa 2):** de los cuatro niveles de abajo,
**Tests unitarios** e **Integración** tienen contenido real hoy.
`tests/integration/` estrenó su primer test en el Bloque A6 — corre
`stream_analysis()` de punta a punta con la pausa de Etapa 2, sin BD real
(CU-02 anónimo). `tests/e2e/` y `tests/regression/` siguen vacíos (solo
`__init__.py`). El job `test` de CI sigue corriendo `pytest -m "unit or
integration"` tolerando exit code 5 (ver `CLAUDE.md`, sección CI) — no se
quitó la tolerancia en el mismo PR que agregó el primer test de
integración, a propósito (un cambio de CI y un cambio de features no van
juntos). Seguimiento de cuándo se cierra cada uno en
`docs/pendientes-tecnicos.md`. Esta sección describe el compromiso
completo de los cuatro niveles — léase como objetivo, no como inventario
de lo que ya existe.

**Corrección 12/08/2026 (Kevin, rediseño del Bloque F del plan de
implementación de Etapa 2):** `tests/regression/` ya no forma parte de este
plan — los tests de regresión matemática contra la tesis los lleva Octavio
por su lado. Sigue vacío en el repo, pero no está huérfano: `docs/plan-etapa2-implementacion.md`
§6 queda como insumo para ese trabajo, no como una tarea pendiente de este
frente. `tests/integration/` sumó dos archivos más en el Bloque F3-F4
(agregación temporal, DECISIÓN 057) — el segundo con nombre expresamente
elegido para dejar constancia del bug real que encontró: rechazar un
atípico de Chow sobre una serie mensual agregada requiere que el índice se
mapee contra la serie agregada (`Etapa1Result.serie_efectiva`), no contra la
serie mensual cruda.

### 1. Tests unitarios del core estadístico

Viven en `tests/unit/core/`. Testean funciones puras de `metis/core/` sin levantar la app.

**Fuente de verdad:** resultados de la tesis de Facundo Ganancias Martínez (2010) sobre 9 estaciones reales de la región sur-oeste de Córdoba. Si METIS produce el mismo resultado que el Excel de Facundo para la misma serie, la implementación es correcta.

```python
# Patrón para cada prueba estadística
def test_anderson_resultado_conocido():
    serie = [72.3, 98.1, 142.5, ...]  # datos reales de la tesis
    resultado = calcular_anderson(serie, alpha=0.05)
    assert resultado.estadistico == pytest.approx(0.23, abs=1e-4)
    assert resultado.valor_critico == pytest.approx(0.37, abs=1e-4)
    assert resultado.veredicto == "aprobada"

# Mismo patrón para: wald_wolfowitz, helmert, t_student, cramer,
# mann_kendall, kolmogorov_smirnov, chow
```

**Criterio de aceptación:** el valor crítico calculado por METIS debe coincidir con el producido por el programa Excel de Facundo para la misma serie de prueba.

### 2. Tests de integración del pipeline

Viven en `tests/integration/`. Levantan la app completa con base de datos de test.

Cubren:
- Pipeline completo Etapa 1 con serie válida
- Pipeline con cada código del catálogo de errores
- Autenticación usuario/contraseña — PENDIENTE hasta confirmar IT (ver docs/decisiones/decision001.md — DECISIÓN 001)
- CU-03 con API Key válida e inválida
- Pausa ante atípico de Chow y reanudación con decisión del usuario
- Persistencia correcta en BD para CU-01
- Ausencia de persistencia para CU-02

### 3. Tests end-to-end por CU

Viven en `tests/e2e/`. Validan flujos completos desde request HTTP hasta response.

Flujos mínimos a cubrir:
- CU-01: autenticación → carga serie → Etapa 1 → Etapa 2 → exportación PDF
- CU-02: carga serie → Etapa 1 → Etapa 2 → verificar que no hay exportación
- CU-03: POST /validate/ con serie válida → verificar estructura JSON completa

### 4. Tests de regresión matemática

Viven en `tests/regression/`. Son los tests más críticos del proyecto.

Comparan resultados de METIS contra los resultados documentados de las 9 estaciones de la tesis. Si algún test de regresión falla, hay un error matemático en la implementación.

```python
# Fixture base — a completar con datos reales de Facundo
ESTACIONES_REFERENCIA = [
    {
        "nombre": "Estacion_01",
        "serie": [...],  # valores reales
        "anderson_esperado": {"estadistico": X, "veredicto": "aprobada"},
        "cramer_esperado": {"n1": X, "n2": X, "veredicto": "aprobada"},
        # etc.
    },
    # ... 8 estaciones más
]

@pytest.mark.parametrize("estacion", ESTACIONES_REFERENCIA)
def test_regresion_etapa1(estacion):
    resultado = ejecutar_etapa1(estacion["serie"])
    assert resultado.anderson.estadistico == pytest.approx(
        estacion["anderson_esperado"]["estadistico"], abs=1e-4
    )
```

**PENDIENTE:** confirmar con Facundo que los datos de las 9 estaciones están disponibles en formato digital para poblar los fixtures.

---

## Testing del frontend

Estrategia separada de los cuatro niveles de arriba — esos son el compromiso
del anteproyecto para el motor estadístico del backend. El frontend tiene su
propia estrategia en capas, escrita como consecuencia directa de
`docs/frontend/informe-diagnostico-ui-rota.md`: dos PRs de frontend se
mergearon a `staging` con CI verde y 98 tests en verde, y la aplicación
estaba rota en uso real (F1 — el stream se abortaba a sí mismo bajo
`StrictMode`, el único modo en que la app corre de verdad en desarrollo, y
ningún test lo ejercitaba). El plan completo de arreglo, con la
justificación detallada de cada capa, vive en
`docs/frontend/plan-arreglo-ui-rota.md` §4.

### Capa 1 — unitarios, bajo StrictMode por regla

`vitest` + Testing Library, un solo mecanismo de mock de red en toda la
suite (`vi.stubGlobal("fetch", ...)` / `vi.mock("@microsoft/fetch-event-source")`
— MSW queda reservado al navegador de dev, nunca a un test, ver DECISIÓN
041). Todo test que renderiza una **página completa** lo hace envuelto en
`<StrictMode>` vía el helper `frontend/src/test/renderPage.tsx` — no opcional
por archivo, es la regla desde `fix/frontend-ui-integracion`. Antes de esto,
`grep -rn "StrictMode" frontend/src` devolvía una sola coincidencia
(`main.tsx`) — el modo en que la app corre en desarrollo no estaba cubierto
por ningún test, y F1 vivía exactamente ahí.

### Capa 2 — integración, componente + hook reales

La capa que faltaba entre "mockeo el hook entero" (`StreamPage.test.tsx`) y
"testeo el hook sin ningún componente" (`sse.test.ts`) — F1 vivía en esa
franja. `StreamPage.integration.test.tsx` monta el componente y el hook
reales, con la red interceptada únicamente en el borde
(`@microsoft/fetch-event-source` mockeado, no MSW — logra lo mismo que el
plan original proponía con MSW-sobre-Node sin apartarse del patrón único de
mock de la Capa 1). `routes.navigation.test.tsx` recorre con clicks el
array `routes` REAL (no rutas de mentira por archivo) — con ese patrón,
"¿existe algún camino de clicks que lleve a `/history`?" pasó de ser una
pregunta imposible de formular a un test real.

### Capa 3 — E2E con Playwright contra Docker (no implementada, requiere decisión)

Propuesta por el plan de arreglo para los defectos que solo son detectables
con el sistema completo corriendo junto (F1, F4, F5, F6, F9 del informe de
diagnóstico). Contradice `constraints.md` — "Scope V1.0 — lo que NO entra"
excluye explícitamente los tests E2E automatizados. **No implementar sin
escribir primero `docs/decisiones/decision046.md`** revisando esa exclusión.

### Capa 4 — cambio de proceso (gratis, y la que más importa)

Definition of done para todo PR que toque `frontend/`: evidencia de haber
corrido el flujo en el navegador después del último commit del PR (captura
o log de la pestaña Network). Ninguna herramienta automática iba a avisar
que `c27d6ac` rompió el stream después de que la verificación manual previa
lo diera por bueno — una casilla en la plantilla de PR, sí.

---

## Análisis estático (también obligatorio)

```bash
# Backend — correr antes de cada commit
ruff check metis/
ruff format metis/

# Frontend — correr antes de cada commit
cd frontend && npm run lint
```

Ambos corren automáticamente en GitHub Actions en cada push.

**SonarCloud** corre además sobre cada PR (`carpinetioctavio/PI_METIS`), vía Análisis Automático
de la App de GitHub de SonarCloud — no hay ningún paso de Sonar en `ci.yml`. Evalúa Reliability
Rating, Security Rating, issues nuevos, duplicación y Security Hotspots; hoy no importa cobertura
porque el Análisis Automático no admite reportes de cobertura (requeriría migrar al scanner
corriendo dentro de CI con un `SONAR_TOKEN` de secret — pendiente, no es una tarea de una sesión de
agente). Ver [DECISIÓN 044](../../docs/decisiones/decision044.md) para el detalle completo,
incluida la configuración en `sonar-project.properties` (raíz del repo) y el estado del check como
consultivo (no bloqueante) en el Ruleset.

---

## Configuración de pytest recomendada

```ini
# pytest.ini
[pytest]
testpaths = tests
asyncio_mode = auto
markers =
    unit: tests unitarios del core (sin BD, sin HTTP)
    integration: tests de integración (con BD de test)
    e2e: tests end-to-end
    regression: tests de regresión matemática contra tesis de Facundo
```

```bash
# Correr solo tests unitarios (rápido, sin dependencias externas)
pytest -m unit

# Correr tests de regresión
pytest -m regresion-unitaria -v

# Todo
pytest -v
```

---

## Base de datos de test

Usar una instancia PostgreSQL separada para tests. Configurar en `.env.test`:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/metis_test
```

Cada test que escribe en BD debe usar transacciones que se revierten al finalizar el test — nunca limpiar manualmente la BD entre tests.

```python
@pytest.fixture(autouse=True)
async def rollback_after_test(db_session):
    yield
    await db_session.rollback()
```

---

---

## Fixtures de tests unitarios

Los fixtures compartidos de tests unitarios viven en 
`tests/unit/core/conftest.py`. Son series sintéticas construidas
ad hoc para forzar comportamientos específicos del pipeline.

`conftest.py` es un mecanismo nativo de pytest — sus fixtures
están disponibles automáticamente para todos los tests del 
directorio sin necesidad de importarlos.

### Fixtures disponibles

**serie_valida** — 35 valores positivos de caudal sin patrones
de tendencia ni autocorrelación. Diseñada para que todas las
pruebas de Etapa 1 aprueben y el pipeline produzca
nivel_confianza="validado". Verificada con smoke test antes
de ser incorporada como fixture.

**serie_valida_corta** — 15 valores del mismo tipo. Suficiente
para superar el mínimo de 10 datos y no ser bloqueante, pero
menor a 30 — activa CONTRACT_LENGTH_WARNING sin detener el
pipeline.

### Criterio para agregar un fixture a conftest.py
Solo si es reutilizado por más de un archivo de test.
Los casos de un solo uso se construyen inline dentro del test.
Todo fixture nuevo debe ser verificado con un smoke test antes
de commitear — ver sección de smoke tests más abajo.

## Smoke tests de desarrollo

Los smoke tests son verificaciones puntuales que se corren manualmente
durante el desarrollo para validar una decisión de implementación antes
de commitear. No son tests formales — no viven en tests/ y no corren en CI.

Se ejecutan directamente desde la terminal:

```bash
cd backend && python3 -c "
from metis.core.pipeline import ejecutar_etapa1
# ... verificación puntual
"
```

Casos donde corresponde correr un smoke test:
- Antes de usar una serie sintética como fixture — verificar que produce
  el resultado esperado
- Después de un cambio en core/ — verificar que el pipeline sigue corriendo
- Ante una duda sobre el comportamiento de una función específica

Los smoke tests no reemplazan los tests formales. Si un smoke test revela
un comportamiento que vale la pena preservar, se convierte en un test
unitario con su caso documentado en el archivo correspondiente.
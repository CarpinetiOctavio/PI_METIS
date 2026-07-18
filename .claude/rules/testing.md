# Estrategia de Testing — METIS

## Cuatro niveles obligatorios (comprometidos en el anteproyecto)

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

## Análisis estático (también obligatorio)

```bash
# Backend — correr antes de cada commit
ruff check metis/
ruff format metis/

# Frontend — correr antes de cada commit
cd frontend && npm run lint
```

Ambos corren automáticamente en GitHub Actions en cada push.

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
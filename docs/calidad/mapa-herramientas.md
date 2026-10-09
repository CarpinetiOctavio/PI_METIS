# Mapa de herramientas de calidad

TP integrador de Calidad de Software, bloque B9. Qué herramienta se usa en cada actividad del ciclo, con la versión
fijada en el repo y dónde está configurada.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

| Actividad | Herramienta | Versión | Configuración | Qué produce |
|---|---|---|---|---|
| **Requisitos** | Manual de Requerimientos (documento escrito) | v5.0 | Fuera del repo | Los 40 RF de `trazabilidad.md` |
| **Planificación y diseño de pruebas** | Markdown versionado en el repo | — | `docs/calidad/` | Plan, riesgos, casos, trazabilidad |
| **Gestión de defectos** | GitHub Issues, plantilla de formulario y labels | — | `.github/ISSUE_TEMPLATE/defecto.yml` | Issues #114 a #123 (`registro-defectos.md`) |
| **Análisis estático — Python** | ruff (lint y formato) | 0.15.12 | Configuración por defecto (sin archivo propio), job `lint` | 0 hallazgos como criterio de merge |
| **Análisis estático — TypeScript** | ESLint y `tsc` | ESLint 9, TypeScript 5.6 | `frontend/eslint.config.js`, `tsconfig*.json`, job `frontend` | ídem |
| **Análisis estático — producto** | SonarCloud (Análisis Automático) | Servicio | `.sonarcloud.properties` | Reliability, Security, hotspots, smells, duplicación. Consultivo hasta B13 |
| **Duplicación** | jscpd | 4.0.5 | `.jscpd.json`, job `quality-gate` | % de líneas duplicadas, umbral 5 % |
| **Consistencia de contratos** | Script propio | — | `scripts/check-error-catalog.sh`, job `error-catalog` | Catálogo de errores sincronizado en tres lugares |
| **Pruebas unitarias — backend** | pytest + pytest-asyncio | 8.2.0 / 0.23.6 | `backend/pytest.ini` (markers `unit`, `integration`, `smoke`, …) | 665 tests |
| **Pruebas unitarias — frontend** | Vitest + Testing Library | Vitest 2.1 | `frontend/vite.config.ts`, helper `src/test/renderPage.tsx` (StrictMode) | 497 tests |
| **Dobles de prueba** | `unittest.mock` (`AsyncMock`); `vi.stubGlobal("fetch")` | — | En cada test | Aislar SMTP, red y base en los tests de unidad |
| **Cobertura** | pytest-cov (`--cov-branch`); `@vitest/coverage-v8` | 5.0.0 / 2.1.9 | Jobs `test` y `frontend` | Sentencia y decisión, XML/lcov y HTML |
| **Cobertura del código nuevo** | diff-cover | 9.2.0 | Job `quality-gate` | Umbral 80 % por PR |
| **Integración** | pytest contra PostgreSQL 15 y Mailpit reales | — | Servicios del job `test`; `tests/integration/db/` | Persistencia, aislamiento y registro de punta a punta |
| **Despliegue** | Docker Compose, nginx | — | `docker-compose.yml` + `docker-compose.ci.yml`, `scripts/deploy-local.sh` | Sistema con la configuración de producción, local y en CI |
| **Smoke** | pytest + httpx contra nginx | httpx 0.27.0 | `backend/tests/smoke/`, job `despliegue` | 7 verificaciones del sistema desplegado |
| **E2E** | Playwright (Chromium) | 1.63.0 | `frontend/playwright.config.ts`, `frontend/e2e/` | 6 escenarios, reporte HTML con trazas y video |
| **Carga y esfuerzo sostenido** | k6 | `grafana/k6:2.3.0` | `carga/k6/`, `carga/umbrales.json`, `scripts/carga.sh`, jobs `carga` y `carga-sostenida.yml` | p95 por endpoint, tasa de error, memoria (`herramienta-carga.md`) |
| **Oráculo de referencia** | Tesis de Facundo; R (`stats`, `randtests`, `Kendall`, `trend`, `lmom`), SciPy | — | `docs/auditoria/comparacion-herramientas/scripts/` | Valores esperados independientes del código de METIS |
| **Integración continua** | GitHub Actions | — | `.github/workflows/ci.yml`, `carga-sostenida.yml` | Siete jobs por push/PR; artefactos y resumen |
| **Métricas** | Script propio | — | `scripts/ci_resumen.py` | `metricas.json` y el resumen del job (`quality-gate`) |
| **Ejecución local de todo** | Script propio | — | `scripts/test.sh` | Lo mismo que el pipeline, por partes o completo |

**Herramienta nueva del TP:** k6, elegida con un proceso de 5 pasos (requisitos, mercado, prueba de concepto contra
Locust, matriz ponderada, despliegue incremental), documentado en `herramienta-carga.md`.

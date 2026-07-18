# DECISIÓN 031 — Reorganización de repo post-cierre de Core Etapa 2
**Fecha:** 18 de Julio de 2026
**Estado:** APLICADA — ver commit [PEGAR HASH ACÁ], "feat(core): cierre de
fase Core Etapa 2 — motor estadístico completo, auditado en 4 fases, más
reorganización de repo pre-commit"

### Contexto
Con las 4 fases de auditoría de Core Etapa 2 cerradas (ver decision013.md
a decision025.md), la estructura de archivos y documentación del repo
había quedado desactualizada durante el desarrollo intensivo del motor
estadístico — nomenclatura inconsistente entre `metis/core/pipeline/` y
sus tests, referencias rotas en `CLAUDE.md`, trazabilidad de auditoría
mezclada con documentación operativa dentro de `.claude/`, y un log de
decisiones monolítico sin separación por archivo. Se dedicó una sesión
completa a reorganizar antes de comitear, para que la estructura fuera
justificable ante el tribunal de ISI — no solo funcional para las
herramientas que operan sobre el repo.

El detalle completo de cada cambio individual está en el mensaje del
commit referenciado arriba, y en las decisiones puntuales que esta
reorganización produjo: [DECISIÓN 026](decision026.md) (ancla de
trazabilidad RF-XXX), [DECISIÓN 027](decision027.md) (rename de
Alembic), [DECISIÓN 028](decision028.md) (gobernanza de ramas),
[DECISIÓN 029](decision029.md) (asignación retroactiva a un fix sin
numerar), [DECISIÓN 030](decision030.md) (decisión de diseño
documentada, pendiente de implementar). Esta entrada no repite esas
justificaciones — deja
evidencia objetiva y verificable de la magnitud del cambio estructural,
con el árbol de archivos real antes y después.

**Nota importante:** el árbol "después" refleja el estado del repo al
cierre de esta sesión, no un estado final — la tesis sigue en curso
(Auth Parte 2, wiring de `services/api`, sesión dedicada de testing, y
cualquier ajuste que surja de las respuestas de Facundo a las preguntas
pendientes en `pendientes-facundo.md` todavía están por delante). Este
árbol es un punto de referencia fechado, no una fotografía definitiva
de la estructura del proyecto.

### Árbol antes (previo a la reorganización - aproximadamente hasta el 15/07/2026)
```
(venv) /Users/octavio/Desktop/PI % tree -a --dirsfirst -I '.git|__pycache__|*.pyc|.pytest_cache|venv|.venv|node_modules|*.egg-info|.ruff_cache|htmlcov|.coverage'
.
├── .claude
│   ├── rules
│   │   ├── auditoria
│   │   │   ├── fases
│   │   │   │   ├── fase1-unitarias.md
│   │   │   │   ├── fase2-cableado.md
│   │   │   │   ├── fase3-testing.md
│   │   │   │   └── fase4-e2e.md
│   │   │   ├── regresion
│   │   │   │   ├── regresion-e2e-coreEstadistico
│   │   │   │   │   ├── consolidacion-e2e.md
│   │   │   │   │   ├── est_01-e2e.md
│   │   │   │   │   ├── est_02-e2e.md
│   │   │   │   │   ├── est_03-e2e.md
│   │   │   │   │   ├── est_04-e2e.md
│   │   │   │   │   ├── est_05-e2e.md
│   │   │   │   │   ├── est_06-e2e.md
│   │   │   │   │   ├── est_07-e2e.md
│   │   │   │   │   ├── est_08-e2e.md
│   │   │   │   │   └── est_09-e2e.md
│   │   │   │   ├── regresion-pipeline
│   │   │   │   │   ├── est_01_alpa_corral_rioBarrancas-pipeline.md
│   │   │   │   │   ├── est_02_vado_rio_seco_rioBarrancas-pipeline.md
│   │   │   │   │   ├── est_03_la_tapa_rioLasCanitas-pipeline.md
│   │   │   │   │   ├── est_04_las_tapias_rioLasTapias-pipeline.md
│   │   │   │   │   ├── est_05_piedra_blanca_rioPiedraBlanca-pipeline.md
│   │   │   │   │   ├── est_06_las_tapias_rioSanBartolome-pipeline.md
│   │   │   │   │   ├── est_07_tincunaco_rioChocancharagua-pipeline.md
│   │   │   │   │   ├── est_08_ume_pay_rioGrande-pipeline.md
│   │   │   │   │   └── est_09_la_suela_rioLaSuela-pipeline.md
│   │   │   │   ├── regresion-unitaria
│   │   │   │   │   ├── est_01_alpa_corral_rioBarrancas-unitaria.md
│   │   │   │   │   ├── est_02_vado_rio_seco_rioBarrancas-unitaria.md
│   │   │   │   │   ├── est_03_la_tapa_rioLasCanitas-unitarias.md
│   │   │   │   │   ├── est_04_las_tapias_rioLasTapias-unitarias.md
│   │   │   │   │   ├── est_05_piedra_blanca_rioPiedraBlanca-unitarias.md
│   │   │   │   │   ├── est_06_las_tapias_rioSanBartolome-unitarias.md
│   │   │   │   │   ├── est_07_tincunaco_rioChocancharagua-unitarias.md
│   │   │   │   │   ├── est_08_ume_pay_rioGrande-unitarias.md
│   │   │   │   │   └── est_09_la_suela_rioLaSuela-unitarias.md
│   │   │   │   └── README.md
│   │   │   ├── decisions-log.md
│   │   │   └── pendientes-facundo.md
│   │   └── docs
│   │       ├── api-contracts.md
│   │       ├── architecture.md
│   │       ├── constraints.md
│   │       ├── core-etapa2-implementation.md
│   │       ├── core-implementation.md
│   │       ├── formulas-etapa1.md
│   │       ├── formulas-etapa2.md
│   │       ├── reimplementacion-etapa2.md
│   │       ├── sprint.md
│   │       ├── statistical-pipeline.md
│   │       └── testing.md
│   └── settings.local.json
├── .github
│   └── workflows
│       └── ci.yml
├── .idea
│   ├── inspectionProfiles
│   │   └── profiles_settings.xml
│   ├── .gitignore
│   ├── PI.iml
│   ├── misc.xml
│   ├── modules.xml
│   ├── vcs.xml
│   └── workspace.xml
├── backend
│   ├── alembic
│   │   ├── versions
│   │   │   ├── 001_baseline_schema.py
│   │   │   ├── 002_add_password_hash_email_verified.py
│   │   │   └── 46f270df2e87_fix_nullability_baseline.py
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── metis
│   │   ├── api
│   │   │   ├── v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis.py
│   │   │   │   └── history.py
│   │   │   ├── __init__.py
│   │   │   └── deps.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   ├── email.py
│   │   │   ├── jwt.py
│   │   │   └── router.py
│   │   ├── core
│   │   │   ├── estadistica_descriptiva
│   │   │   │   ├── __init__.py
│   │   │   │   └── descriptive.py
│   │   │   ├── etapa1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── homogeneity.py
│   │   │   │   ├── independence.py
│   │   │   │   ├── outliers.py
│   │   │   │   └── trend.py
│   │   │   ├── etapa2
│   │   │   │   ├── distributions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── exponencial_beta.py
│   │   │   │   │   ├── exponencial_x0_beta.py
│   │   │   │   │   ├── gamma2p.py
│   │   │   │   │   ├── gamma3p.py
│   │   │   │   │   ├── gen_exponencial.py
│   │   │   │   │   ├── gen_pareto.py
│   │   │   │   │   ├── gumbel.py
│   │   │   │   │   ├── gve.py
│   │   │   │   │   ├── lognormal2p.py
│   │   │   │   │   ├── lognormal3p.py
│   │   │   │   │   ├── logpearson3.py
│   │   │   │   │   ├── normal.py
│   │   │   │   │   └── uniforme.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── eea.py
│   │   │   │   ├── empirical.py
│   │   │   │   ├── pipeline2.py
│   │   │   │   ├── types.py
│   │   │   │   └── utils.py
│   │   │   ├── pipeline
│   │   │   │   ├── __init__.py
│   │   │   │   └── pipeline.py
│   │   │   ├── validacion
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contract.py
│   │   │   │   └── parser.py
│   │   │   ├── __init__.py
│   │   │   ├── types.py
│   │   │   └── utils.py
│   │   ├── db
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis.py
│   │   │   │   ├── api_client.py
│   │   │   │   ├── result.py
│   │   │   │   └── user.py
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   ├── auth.py
│   │   │   └── common.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   └── session_store.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests
│   │   ├── e2e
│   │   │   └── __init__.py
│   │   ├── integration
│   │   │   └── __init__.py
│   │   ├── regression
│   │   │   └── __init__.py
│   │   ├── unit
│   │   │   ├── core
│   │   │   │   ├── etapa2
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_exponencial_x0_beta.py
│   │   │   │   │   ├── test_gamma2p.py
│   │   │   │   │   ├── test_gamma3p.py
│   │   │   │   │   ├── test_gen_pareto.py
│   │   │   │   │   ├── test_gumbel.py
│   │   │   │   │   ├── test_gve.py
│   │   │   │   │   ├── test_lognormal3p.py
│   │   │   │   │   └── test_logpearson3.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   ├── test_contract.py
│   │   │   │   ├── test_descriptive.py
│   │   │   │   ├── test_homogeneity.py
│   │   │   │   ├── test_independence.py
│   │   │   │   ├── test_outliers.py
│   │   │   │   ├── test_pipeline.py
│   │   │   │   └── test_trend.py
│   │   │   ├── services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   └── test_analysis_service.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── frontend
│   └── README.md
├── nginx
│   └── nginx.conf
├── .DS_Store
├── .env
├── .env.example
├── .gitignore
├── CLAUDE.md
└── docker-compose.yml

42 directories, 162 files
```

### Árbol posterior al 18/07/2026 (post-reorganización, al momento de este commit)
```
(venv) /Users/octavio/Desktop/PI %  tree -a --dirsfirst -I '.git|__pycache__|*.pyc|.pytest_cache|venv|.venv|node_modules|*.egg-info|.ruff_cache|htmlcov|.coverage'
.
├── .claude
│   ├── rules
│   │   ├── architecture
│   │   │   ├── api-contracts.md
│   │   │   ├── architecture.md
│   │   │   └── constraints.md
│   │   ├── core
│   │   │   ├── core-etapa1-implementation.md
│   │   │   ├── core-etapa2-implementation.md
│   │   │   ├── formulas-etapa1.md
│   │   │   ├── formulas-etapa2.md
│   │   │   └── statistical-pipeline.md
│   │   ├── sprint.md
│   │   └── testing.md
│   └── settings.local.json
├── .github
│   └── workflows
│       └── ci.yml
├── .idea
│   ├── inspectionProfiles
│   │   └── profiles_settings.xml
│   ├── .gitignore
│   ├── PI.iml
│   ├── misc.xml
│   ├── modules.xml
│   ├── vcs.xml
│   └── workspace.xml
├── backend
│   ├── alembic
│   │   ├── versions
│   │   │   ├── 001_baseline_schema.py
│   │   │   ├── 002_add_password_hash_email_verified.py
│   │   │   └── 003_fix_nullability_baseline.py
│   │   ├── README
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── metis
│   │   ├── api
│   │   │   ├── v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis.py
│   │   │   │   └── history.py
│   │   │   ├── __init__.py
│   │   │   └── deps.py
│   │   ├── auth
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   ├── email.py
│   │   │   ├── jwt.py
│   │   │   └── router.py
│   │   ├── core
│   │   │   ├── estadistica_descriptiva
│   │   │   │   ├── __init__.py
│   │   │   │   └── descriptive.py
│   │   │   ├── etapa1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── homogeneity.py
│   │   │   │   ├── independence.py
│   │   │   │   ├── outliers.py
│   │   │   │   └── trend.py
│   │   │   ├── etapa2
│   │   │   │   ├── distributions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── exponencial_beta.py
│   │   │   │   │   ├── exponencial_x0_beta.py
│   │   │   │   │   ├── gamma2p.py
│   │   │   │   │   ├── gamma3p.py
│   │   │   │   │   ├── gen_exponencial.py
│   │   │   │   │   ├── gen_pareto.py
│   │   │   │   │   ├── gumbel.py
│   │   │   │   │   ├── gve.py
│   │   │   │   │   ├── lognormal2p.py
│   │   │   │   │   ├── lognormal3p.py
│   │   │   │   │   ├── logpearson3.py
│   │   │   │   │   ├── normal.py
│   │   │   │   │   └── uniforme.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── eea.py
│   │   │   │   ├── empirical.py
│   │   │   │   ├── types.py
│   │   │   │   └── utils.py
│   │   │   ├── pipeline
│   │   │   │   ├── __init__.py
│   │   │   │   ├── full_pipeline.py
│   │   │   │   ├── pipeline_etapa1.py
│   │   │   │   ├── pipeline_etapa2.py
│   │   │   │   └── types.py
│   │   │   ├── validacion
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contract.py
│   │   │   │   └── parser.py
│   │   │   ├── __init__.py
│   │   │   ├── types.py
│   │   │   └── utils.py
│   │   ├── db
│   │   │   ├── models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analysis.py
│   │   │   │   ├── api_client.py
│   │   │   │   ├── result.py
│   │   │   │   └── user.py
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   ├── auth.py
│   │   │   └── common.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   └── session_store.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests
│   │   ├── e2e
│   │   │   └── __init__.py
│   │   ├── integration
│   │   │   └── __init__.py
│   │   ├── regression
│   │   │   └── __init__.py
│   │   ├── unit
│   │   │   ├── core
│   │   │   │   ├── estadistica_descriptiva
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── test_descriptive.py
│   │   │   │   ├── etapa1
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_homogeneity.py
│   │   │   │   │   ├── test_independence.py
│   │   │   │   │   ├── test_outliers.py
│   │   │   │   │   └── test_trend.py
│   │   │   │   ├── etapa2
│   │   │   │   │   ├── distributions
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── test_exponencial_x0_beta.py
│   │   │   │   │   │   ├── test_gamma2p.py
│   │   │   │   │   │   ├── test_gamma3p.py
│   │   │   │   │   │   ├── test_gen_pareto.py
│   │   │   │   │   │   ├── test_gumbel.py
│   │   │   │   │   │   ├── test_gve.py
│   │   │   │   │   │   ├── test_lognormal3p.py
│   │   │   │   │   │   └── test_logpearson3.py
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── pipeline
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── test_full_pipeline.py
│   │   │   │   │   ├── test_pipeline_etapa1.py
│   │   │   │   │   └── test_pipeline_etapa2.py
│   │   │   │   ├── validacion
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── test_contract.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── conftest.py
│   │   │   ├── services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conftest.py
│   │   │   │   └── test_analysis_service.py
│   │   │   └── __init__.py
│   │   ├── README.md
│   │   └── __init__.py
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── docs
│   ├── auditoria
│   │   ├── fases
│   │   │   ├── fase1-unitarias.md
│   │   │   ├── fase2-cableado.md
│   │   │   ├── fase3-testing.md
│   │   │   ├── fase4-e2e-coreEstadistico.md
│   │   │   └── pendientes-cableado-fase2.md
│   │   ├── pendientes
│   │   │   └── pendientes-facundo.md
│   │   └── regresion
│   │       ├── regresion-e2e-coreEstadistico
│   │       │   ├── consolidacion-e2e.md
│   │       │   ├── est_01-e2e.md
│   │       │   ├── est_02-e2e.md
│   │       │   ├── est_03-e2e.md
│   │       │   ├── est_04-e2e.md
│   │       │   ├── est_05-e2e.md
│   │       │   ├── est_06-e2e.md
│   │       │   ├── est_07-e2e.md
│   │       │   ├── est_08-e2e.md
│   │       │   └── est_09-e2e.md
│   │       ├── regresion-pipeline
│   │       │   ├── est_01_alpa_corral_rioBarrancas-pipeline.md
│   │       │   ├── est_02_vado_rio_seco_rioBarrancas-pipeline.md
│   │       │   ├── est_03_la_tapa_rioLasCanitas-pipeline.md
│   │       │   ├── est_04_las_tapias_rioLasTapias-pipeline.md
│   │       │   ├── est_05_piedra_blanca_rioPiedraBlanca-pipeline.md
│   │       │   ├── est_06_las_tapias_rioSanBartolome-pipeline.md
│   │       │   ├── est_07_tincunaco_rioChocancharagua-pipeline.md
│   │       │   ├── est_08_ume_pay_rioGrande-pipeline.md
│   │       │   └── est_09_la_suela_rioLaSuela-pipeline.md
│   │       ├── regresion-unitaria
│   │       │   ├── est_01_alpa_corral_rioBarrancas-unitaria.md
│   │       │   ├── est_02_vado_rio_seco_rioBarrancas-unitaria.md
│   │       │   ├── est_03_la_tapa_rioLasCanitas-unitaria.md
│   │       │   ├── est_04_las_tapias_rioLasTapias-unitaria.md
│   │       │   ├── est_05_piedra_blanca_rioPiedraBlanca-unitaria.md
│   │       │   ├── est_06_las_tapias_rioSanBartolome-unitaria.md
│   │       │   ├── est_07_tincunaco_rioChocancharagua-unitaria.md
│   │       │   ├── est_08_ume_pay_rioGrande-unitaria.md
│   │       │   └── est_09_la_suela_rioLaSuela-unitaria.md
│   │       └── README.md
│   ├── decisiones
│   │   ├── README.md
│   │   ├── decision001.md
│   │   ├── decision002.md
│   │   ├── decision003.md
│   │   ├── decision004.md
│   │   ├── decision005.md
│   │   ├── decision006.md
│   │   ├── decision007.md
│   │   ├── decision008.md
│   │   ├── decision009.md
│   │   ├── decision010.md
│   │   ├── decision011.md
│   │   ├── decision012.md
│   │   ├── decision013.md
│   │   ├── decision014.md
│   │   ├── decision015.md
│   │   ├── decision016.md
│   │   ├── decision017.md
│   │   ├── decision018.md
│   │   ├── decision019.md
│   │   ├── decision020.md
│   │   ├── decision021.md
│   │   ├── decision022.md
│   │   ├── decision023.md
│   │   ├── decision024.md
│   │   ├── decision025.md
│   │   ├── decision026.md
│   │   ├── decision027.md
│   │   ├── decision028.md
│   │   ├── decision029.md
│   │   ├── decision030.md
│   │   └── decision031.md
│   ├── historico
│   │   ├── README.md
│   │   ├── oauth-descartado.md
│   │   └── reimplementacion-etapa2.md
│   └── README.md
├── frontend
│   └── README.md
├── nginx
│   └── nginx.conf
├── .DS_Store
├── .env
├── .env.example
├── .gitignore
├── CLAUDE.md
└── docker-compose.yml

52 directories, 206 files
```
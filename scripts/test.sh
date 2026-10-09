#!/usr/bin/env bash
# Un solo comando para las pruebas de METIS (B1a del plan del TP de Calidad, DECISIÓN 077).
#
#   scripts/test.sh unit         tests unitarios del backend
#   scripts/test.sh integration  tests de integración del backend
#   scripts/test.sh backend      unit + integration con cobertura (sentencia y decisión)
#   scripts/test.sh frontend     Vitest con cobertura
#   scripts/test.sh duplicacion  jscpd sobre backend/metis y frontend/src (umbral 5 %)
#   scripts/test.sh gate         cobertura del código nuevo contra origin/staging (diff-cover ≥ 80 %)
#   scripts/test.sh all          backend + frontend + duplicacion
#   scripts/test.sh smoke        smoke del despliegue contra nginx (requiere scripts/deploy-local.sh)
#   scripts/test.sh e2e [spec]   Playwright contra el despliegue (requiere scripts/deploy-local.sh)
#
# stress y soak se suman con el bloque B7.
#
# Backend: usa el Python activo si tiene las dependencias de requirements.txt; si no, corre dentro
# del contenedor `backend` de docker compose (reconstruirlo si requirements.txt cambió:
# `docker compose build backend`). Los reportes quedan en backend/ y frontend/coverage/.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

pytest_backend() {
  if (cd backend && python -c "import sqlalchemy, pytest_cov" 2>/dev/null); then
    (cd backend && python -m pytest "$@")
  else
    echo "Python local sin dependencias: corriendo en el contenedor backend." >&2
    docker compose run --rm --no-deps backend pytest "$@"
  fi
}

COBERTURA=(--cov=metis --cov-branch --cov-report=term --cov-report=xml --cov-report=html)

case "${1:-}" in
  unit)
    pytest_backend -m unit
    ;;
  integration)
    pytest_backend -m integration
    ;;
  backend)
    pytest_backend -m "unit or integration" "${COBERTURA[@]}" --junitxml=junit-backend.xml
    ;;
  frontend)
    (cd frontend && npm run test:coverage)
    ;;
  duplicacion)
    [[ -x frontend/node_modules/.bin/jscpd ]] || (cd frontend && npm ci --ignore-scripts)
    frontend/node_modules/.bin/jscpd backend/metis frontend/src
    ;;
  gate)
    command -v diff-cover >/dev/null || { echo "Falta diff-cover: pip install --only-binary :all: diff-cover==9.2.0" >&2; exit 1; }
    git fetch -q origin staging
    diff-cover backend/coverage.xml --compare-branch=origin/staging --fail-under=80
    sed -E -e '/^SF:/s#[\]#/#g' -e 's#^SF:src/#SF:frontend/src/#' frontend/coverage/lcov.info > frontend/coverage/lcov-repo.info
    diff-cover frontend/coverage/lcov-repo.info --compare-branch=origin/staging --fail-under=80
    ;;
  all)
    "$0" backend
    "$0" frontend
    "$0" duplicacion
    ;;
  smoke)
    # Black-box contra nginx: desde el Python local si tiene httpx y pytest; si no, desde un contenedor
    # efímero en la red del despliegue (nginx se llama `nginx` ahí adentro).
    if (cd backend && python -c "import httpx, pytest" 2>/dev/null); then
      (cd backend && METIS_REQUIRE_SMOKE=1 python -m pytest -m smoke tests/smoke -v)
    else
      echo "Python local sin httpx/pytest: corriendo el smoke en un contenedor." >&2
      COMPOSE_PATH_SEPARATOR=";" COMPOSE_FILE="docker-compose.yml;docker-compose.ci.yml" \
        docker compose -p metis-ci run --rm --no-deps -e METIS_REQUIRE_SMOKE=1 \
        -e SMOKE_BASE_URL=http://nginx -e SMOKE_EMAIL -e SMOKE_PASSWORD \
        backend pytest -m smoke tests/smoke -v
    fi
    ;;
  e2e)
    # El usuario que siembra scripts/deploy-local.sh (el mismo del smoke).
    export E2E_EMAIL="${E2E_EMAIL:-${SMOKE_EMAIL:-smoke@ucc.edu.ar}}"
    export E2E_PASSWORD="${E2E_PASSWORD:-${SMOKE_PASSWORD:-smoke-metis-1234}}"
    (cd frontend && npm run test:e2e -- "${@:2}")
    ;;
  stress | soak)
    echo "'$1' todavía no existe: llega con el bloque B7." >&2
    exit 2
    ;;
  *)
    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac

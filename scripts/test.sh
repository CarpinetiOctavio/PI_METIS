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
#
# smoke, e2e, stress y soak se suman con los bloques B5, B6 y B7.
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
  smoke | e2e | stress | soak)
    echo "'$1' todavía no existe: llega con el bloque B5 (smoke), B6 (e2e) o B7 (stress, soak)." >&2
    exit 2
    ;;
  *)
    sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac

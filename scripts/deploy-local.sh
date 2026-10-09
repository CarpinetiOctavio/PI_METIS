#!/usr/bin/env bash
# Despliegue desde cero con la configuración de producción (B5 del plan del TP de Calidad). Es el mismo
# procedimiento en la máquina local (demo) y en el job `despliegue` de CI:
#
#   1. baja el stack anterior y borra su base (solo la del proyecto metis-ci, no la de desarrollo)
#   2. construye las imágenes y levanta todo con docker-compose.ci.yml (sin --reload ni bind mount)
#   3. aplica las migraciones (paso explícito: nada en la app lo hace solo)
#   4. espera que nginx responda /ping
#   5. siembra un usuario verificado para el smoke
#   6. corre el smoke contra nginx (scripts/test.sh smoke)
#
# Uso:
#   scripts/deploy-local.sh             todo, smoke incluido
#   scripts/deploy-local.sh --sin-smoke despliega y siembra, sin el smoke
#   scripts/deploy-local.sh --bajar     baja el stack y borra su base
#
# Queda en http://localhost (nginx) y http://localhost:8025 (Mailpit). Ocupa el puerto 80: si el stack de
# desarrollo está arriba, bajarlo antes con `docker compose down` (sin -v, no pierde datos).
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

# Toda llamada a `docker compose` de este script y de los que llama (seed-dev-user.sh) apunta al stack de
# despliegue. El separador explícito hace que COMPOSE_FILE valga igual en Linux y en Windows.
export COMPOSE_PATH_SEPARATOR=";"
export COMPOSE_FILE="docker-compose.yml;docker-compose.ci.yml"
export COMPOSE_PROJECT_NAME="metis-ci"

BASE_URL="${SMOKE_BASE_URL:-http://localhost}"
export SMOKE_EMAIL="${SMOKE_EMAIL:-smoke@ucc.edu.ar}"
export SMOKE_PASSWORD="${SMOKE_PASSWORD:-smoke-metis-1234}"

if [[ "${1:-}" == "--bajar" ]]; then
  docker compose down -v --remove-orphans
  exit 0
fi

echo "== 1/6 Bajando el despliegue anterior"
docker compose down -v --remove-orphans

echo "== 2/6 Construyendo y levantando (docker-compose.ci.yml)"
docker compose up -d --build --wait

echo "== 3/6 Migraciones"
docker compose exec -T backend alembic upgrade head

echo "== 4/6 Esperando ${BASE_URL}/ping"
for _ in $(seq 1 60); do
  if curl -fsS "${BASE_URL}/ping" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS "${BASE_URL}/ping" >/dev/null || {
  echo "nginx no responde ${BASE_URL}/ping" >&2
  docker compose logs --tail 50 >&2
  exit 1
}

echo "== 5/6 Usuario del smoke"
bash scripts/seed-dev-user.sh "$SMOKE_EMAIL" "$SMOKE_PASSWORD" "Usuario del smoke"

if [[ "${1:-}" == "--sin-smoke" ]]; then
  echo "Desplegado en ${BASE_URL} (smoke salteado)."
  exit 0
fi

echo "== 6/6 Smoke"
SMOKE_BASE_URL="$BASE_URL" bash scripts/test.sh smoke
echo "Desplegado en ${BASE_URL} y smoke en verde."

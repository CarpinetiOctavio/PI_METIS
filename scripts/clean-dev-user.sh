#!/usr/bin/env bash
# Contraparte de seed-dev-user.sh. Borra los análisis del usuario (la tabla
# analysis_results se limpia sola por ON DELETE CASCADE) y el usuario mismo.
#
# Uso: ./scripts/clean-dev-user.sh [email]
set -euo pipefail
cd "$(dirname "$0")/.."

EMAIL="${1:-2200001@ucc.edu.ar}"

docker compose exec -T postgres psql -U metis_user -d metis -v ON_ERROR_STOP=1 -c "
DELETE FROM analyses WHERE user_id = (SELECT id FROM users WHERE email = '${EMAIL}');
DELETE FROM users WHERE email = '${EMAIL}';
"

echo "Usuario ${EMAIL} y sus análisis eliminados (si existían)."

#!/usr/bin/env bash
# Automatiza el INSERT bcrypt que sprint.md ya documenta en prosa
# (actualización 29/07/2026): sin SMTP real, POST /auth/register no crea
# ningún usuario (falla con AUTH_VERIFICATION_EMAIL_FAILED antes del commit
# — DECISIÓN 032). Este script es la vía (a) de la sección 1.3 del plan de
# arreglo — desbloquea login/logout/me/historial/persistencia (CU-01
# completo) sin ninguna decisión de arquitectura pendiente.
#
# Usa `docker compose exec <servicio>` en vez de nombres de contenedor
# hardcodeados — el prefijo del contenedor lo decide Docker Compose a partir
# del nombre del directorio y ya cambió una vez en este repo (ver sprint.md).
#
# Uso:
#   ./scripts/seed-dev-user.sh [email] [password] [nombre]
# Requiere:
#   docker compose up -d backend postgres
set -euo pipefail
cd "$(dirname "$0")/.."

EMAIL="${1:-2200001@ucc.edu.ar}"
PASSWORD="${2:-test1234}"
NOMBRE="${3:-Usuario de Prueba}"

if [[ "$EMAIL" != *@ucc.edu.ar ]]; then
  echo "El email debe terminar en @ucc.edu.ar (contrato de auth/register)." >&2
  exit 1
fi

HASH=$(docker compose exec -T backend python3 -c \
  "import bcrypt; print(bcrypt.hashpw(b'${PASSWORD}', bcrypt.gensalt()).decode())")

docker compose exec -T postgres psql -U metis_user -d metis -v ON_ERROR_STOP=1 -c \
  "INSERT INTO users (id, email, nombre, password_hash, email_verified, created_at)
   VALUES (gen_random_uuid(), '${EMAIL}', '${NOMBRE}', '${HASH}', true, now());"

echo
echo "Usuario de desarrollo creado:"
echo "  email:    ${EMAIL}"
echo "  password: ${PASSWORD}"
echo
echo "Limpiar con: ./scripts/clean-dev-user.sh ${EMAIL}"

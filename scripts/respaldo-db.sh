#!/usr/bin/env bash
# Respaldo de la base de METIS (B5 del plan de mejoras post-despliegue UCC, hallazgo H9). Pensado para correr
# desde cron en el servidor, en el directorio del compose:
#   scripts/respaldo-db.sh [directorio]
#
# COMPOSE_FILE va en el .env del servidor, que compose lee solo: no hace falta exportarlo en el cron.
#
# Deja metis_<fecha>.sql.gz en el directorio (por defecto respaldos/, ignorado por git) y borra los de más de
# RETENCION_DIAS días (7 por defecto). pg_dump en formato plano: se restaura con psql, sin herramientas extra.
# Restauración de prueba documentada en docs/calidad/despliegue-ucc.md §5.
set -euo pipefail

DESTINO="${1:-respaldos}"
RETENCION_DIAS="${RETENCION_DIAS:-7}"
mkdir -p "$DESTINO"

archivo="$DESTINO/metis_$(date +%Y-%m-%d_%H%M).sql.gz"
# El usuario y la base salen del entorno del contenedor de postgres (el .env del servidor): no se repiten acá.
# -T: sin TTY, para que cron no corte la salida. El .partial evita dejar un respaldo truncado con nombre válido.
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner' \
  | gzip > "$archivo.partial"
mv "$archivo.partial" "$archivo"

find "$DESTINO" -name 'metis_*.sql.gz' -mtime +"$RETENCION_DIAS" -delete
echo "Respaldo en $archivo ($(du -h "$archivo" | cut -f1))."

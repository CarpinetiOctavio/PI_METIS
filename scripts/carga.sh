#!/usr/bin/env bash
# Pruebas de carga con k6 (B7 del plan del TP de Calidad, DECISIÓN 077) contra el despliegue de
# scripts/deploy-local.sh. k6 corre en un contenedor dentro de la red del despliegue y le pega a
# nginx, como cualquier cliente. Los umbrales están en carga/umbrales.json.
#
#   scripts/carga.sh quiebre              rampa de 10 a 120 usuarios; tabla por minuto (exploratorio)
#   scripts/carga.sh ci                   carga fija con umbrales: falla si se superan
#   scripts/carga.sh sostenido [30m]      carga moderada y constante + memoria del backend
#
# Resultados en carga/resultados/<perfil>-<fecha>/: resumen.txt, resumen.json (--summary-export),
# k6.csv.gz, reporte.html (dashboard de k6) y, en sostenido, memoria.csv.
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"

PERFIL="${1:-}"
case "$PERFIL" in
  quiebre | ci) SCRIPT=stress.js ;;
  sostenido) SCRIPT=sostenido.js ;;
  *)
    sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac

K6_IMAGEN="grafana/k6:2.3.0"
RED="metis-ci_default"
CORRIDA="${PERFIL}-$(date +%Y%m%d-%H%M%S)"
SALIDA="carga/resultados/$CORRIDA"
mkdir -p "$SALIDA"
# El contenedor de k6 corre con un usuario propio sin privilegios (uid 12345): necesita poder escribir los
# resultados en la carpeta que creó el usuario del host.
chmod a+rwx "$SALIDA"
PY="$(command -v python3 || command -v python)"

# Docker Desktop en Windows necesita la ruta en formato Windows para el volumen.
CARGA="$RAIZ/carga"
command -v cygpath >/dev/null && CARGA="$(cygpath -w "$CARGA")"

docker network inspect "$RED" >/dev/null 2>&1 || {
  echo "No hay despliegue en la red $RED: correr antes scripts/deploy-local.sh" >&2
  exit 1
}

DURACION="${2:-30m}"
[[ "$DURACION" =~ ^[0-9]+[smh]$ ]] || { echo "Duración inválida: '$DURACION' (ejemplos: 30m, 1h)" >&2; exit 1; }

MUESTREO_PID=""
if [[ "$PERFIL" == "sostenido" ]]; then
  BACKEND="$(docker ps -q --filter "label=com.docker.compose.project=metis-ci" --filter "label=com.docker.compose.service=backend")"
  # Una muestra cada 15 s: epoch,MiB. docker stats informa "123.4MiB / 7.6GiB".
  (
    while true; do
      uso="$(docker stats --no-stream --format '{{.MemUsage}}' "$BACKEND" | awk '{print $1}')"
      awk -v t="$(date +%s)" -v u="$uso" 'BEGIN {
        n = u + 0; f = 1
        if (u ~ /GiB$/) f = 1024; else if (u ~ /KiB$/) f = 1 / 1024
        printf "%d,%.1f\n", t, n * f
      }' >> "$SALIDA/memoria.csv"
      sleep 15
    done
  ) &
  MUESTREO_PID=$!
fi

set +e
MSYS_NO_PATHCONV=1 docker run --rm --network "$RED" -v "$CARGA:/carga" \
  -e BASE_URL=http://nginx -e PERFIL="$PERFIL" -e DURACION="$DURACION" \
  -e K6_WEB_DASHBOARD=true -e K6_WEB_DASHBOARD_EXPORT="/carga/${SALIDA#carga/}/reporte.html" \
  "$K6_IMAGEN" run --quiet \
  --summary-export "/carga/${SALIDA#carga/}/resumen.json" \
  --out "csv=/carga/${SALIDA#carga/}/k6.csv.gz" \
  "/carga/k6/$SCRIPT" | tee "$SALIDA/resumen.txt"
CODIGO=${PIPESTATUS[0]}
set -e

[[ -n "$MUESTREO_PID" ]] && kill "$MUESTREO_PID" 2>/dev/null || true

case "$PERFIL" in
  quiebre)
    "$PY" carga/analizar.py escalones "$CORRIDA" | tee "$SALIDA/escalones.md"
    echo "Quiebre: exploratorio, no falla por umbrales (k6 salió con $CODIGO). Resultados en $SALIDA"
    exit 0
    ;;
  sostenido)
    set +e
    "$PY" carga/analizar.py memoria "$CORRIDA" | tee "$SALIDA/memoria.txt"
    MEM=${PIPESTATUS[0]}
    set -e
    [[ $CODIGO -eq 0 && $MEM -eq 0 ]] || exit 1
    ;;
  *)
    exit "$CODIGO"
    ;;
esac

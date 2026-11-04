#!/usr/bin/env bash
# Genera el certificado autofirmado del servidor de la UCC (DECISIÓN 083, parte 2) en certs/metis.crt y
# certs/metis.key. Corre en el servidor, en el directorio del compose; certs/ está ignorado por git.
#
# Uso: scripts/generar-cert-ucc.sh [IP] [dias] [nombre ...]
#   IP      por defecto 172.16.168.14
#   dias    por defecto 3650 (el certificado no es de confianza para nadie: Cloudflare en modo "Full" no lo
#           valida, así que no hay nada que renovar; una vigencia larga evita un vencimiento por olvido)
#   nombre  nombres DNS adicionales para el SAN, por ejemplo el de Cloudflare
#
# No pisa un certificado existente: borrar certs/metis.* a propósito para regenerarlo.
set -euo pipefail

IP="${1:-172.16.168.14}"
DIAS="${2:-3650}"
shift 2 2>/dev/null || shift $# 2>/dev/null || true

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/certs"
mkdir -p "$DIR"

if [[ -e "$DIR/metis.crt" || -e "$DIR/metis.key" ]]; then
  echo "Ya existe un certificado en $DIR. Borrarlo a propósito para regenerarlo." >&2
  exit 1
fi

SAN="IP:${IP},DNS:metis.local"
for n in "$@"; do SAN+=",DNS:${n}"; done

# Clave RSA 2048 sin contraseña (nginx tiene que poder arrancar solo tras un reinicio).
openssl req -x509 -newkey rsa:2048 -nodes -sha256 -days "$DIAS" \
  -keyout "$DIR/metis.key" -out "$DIR/metis.crt" \
  -subj "/O=METIS/CN=${IP}" \
  -addext "subjectAltName=${SAN}" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "keyUsage=critical,digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth"

chmod 600 "$DIR/metis.key"
chmod 644 "$DIR/metis.crt"

echo "Certificado generado en $DIR (SAN: ${SAN}, ${DIAS} días)."
openssl x509 -in "$DIR/metis.crt" -noout -subject -enddate -fingerprint -sha256

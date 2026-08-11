#!/usr/bin/env bash
# Chequeo bidireccional (en realidad tridireccional) del catálogo de
# códigos de error — DECISIÓN 038 (docs/decisiones/decision038.md) y su
# addendum del 29/07/2026 (M2, pasada 3 de mejora del frontend).
#
# Verifica que:
#   1. Todo código que el backend emite está en el catálogo.
#   2. Todo código del catálogo está en el diccionario del frontend.
#   3. Todo código del diccionario del frontend está en el catálogo.
#
# Corre desde la raíz del repo: ./scripts/check-error-catalog.sh
#
# Heurístico, no un parser real — ancla los prefijos de código conocidos.
# Si se agrega una familia de códigos con un prefijo nuevo, agregarlo acá
# Y en el regex de docs/decisiones/decision038.md (el addendum documenta
# esta misma limitación).
set -euo pipefail

cd "$(dirname "$0")/.."

PREFIXES="AUTH|CONTRACT|TEST|DIST|PARSE|SESSION"
PREFIXES_WITH_FRONTEND="${PREFIXES}|VALIDATION|STREAM"

ALLOWLIST="scripts/error-catalog-allowlist.txt"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# Códigos que el backend emite — solo los seis prefijos de servidor,
# VALIDATION_/STREAM_ son exclusivamente de frontend por diseño.
grep -rhoE "\"(${PREFIXES})_[A-Z_]+\"" backend/metis/ \
  | tr -d '"' | sort -u > "$TMPDIR/emit.txt"

# Códigos en el catálogo — incluye los prefijos de frontend, porque
# api-contracts.md sí documenta VALIDATION_ERROR/STREAM_CONNECTION_ERROR.
grep -ohE "\\b(${PREFIXES_WITH_FRONTEND})_[A-Z_]+" \
  .claude/rules/architecture/api-contracts.md | sort -u > "$TMPDIR/cat.txt"

# Códigos en el diccionario del frontend.
grep -ohE '^  [A-Z_]+:' frontend/src/i18n/errors.es.ts \
  | tr -d ' :' | sort -u > "$TMPDIR/fe.txt"

# Allowlist — sin comentarios ni líneas vacías.
# || true — un allowlist vacío (sin excepciones activas, el caso ideal) no
# tiene ninguna línea que matchee "no es comentario ni vacía", y grep sale
# con status 1 por "sin resultados" bajo set -e sin esto, abortando el
# script entero antes de correr ningún chequeo real.
grep -vE '^\s*(#|$)' "$ALLOWLIST" | sort -u > "$TMPDIR/allow.txt" || true

FAILED=0

check_direction() {
  local label="$1" left="$2" right="$3"
  local diff
  diff=$(comm -23 "$left" "$right" | comm -23 - "$TMPDIR/allow.txt" || true)
  if [[ -n "$diff" ]]; then
    {
      echo "FAIL — $label:"
      echo "$diff" | sed 's/^/  /'
    } >&2
    FAILED=1
  else
    echo "OK — $label"
  fi
}

check_direction "backend emite, ausente del catálogo" \
  "$TMPDIR/emit.txt" "$TMPDIR/cat.txt"
check_direction "catálogo, ausente del diccionario del frontend" \
  "$TMPDIR/cat.txt" "$TMPDIR/fe.txt"
check_direction "diccionario del frontend, ausente del catálogo" \
  "$TMPDIR/fe.txt" "$TMPDIR/cat.txt"

if [[ "$FAILED" -ne 0 ]]; then
  {
    echo
    echo "Hay códigos de error sin catalogar en alguna dirección. Agregarlos a"
    echo ".claude/rules/architecture/api-contracts.md y/o frontend/src/i18n/errors.es.ts,"
    echo "o a scripts/error-catalog-allowlist.txt con un comentario que justifique"
    echo "por qué la excepción es legítima (ver DECISIÓN 038)."
  } >&2
  exit 1
fi

echo >&2
echo "Catálogo de códigos de error sincronizado en las tres direcciones." >&2

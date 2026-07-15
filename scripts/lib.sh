#!/usr/bin/env bash
# lib.sh — helpers compartidos para la operacion del tunel Cloudflare.
# Se hace `source` desde los demas scripts. No ejecutar directo.

set -euo pipefail

# --- Identidad del tunel (estandar: <repo-slug>-<env>) ---
TUNNEL_NAME="${TUNNEL_NAME:-moderation-dev}"
TUNNEL_HOSTNAME="${TUNNEL_HOSTNAME:-dev-moderation.josuesay.com}"

CLOUDFLARED_CONFIG_DIR="${HOME}/.cloudflared"
CLOUDFLARED_CONFIG_FILE="${CLOUDFLARED_CONFIG_DIR}/${TUNNEL_NAME}.yml"

# QUIC falla en la version instalada de cloudflared (CRYPTO_ERROR 0x178);
# forzamos http2. Ver skill cloudflare-tunnel-standards / troubleshooting.
TUNNEL_PROTOCOL="${TUNNEL_PROTOCOL:-http2}"

# Puerto local del Provider: se lee de config.yml (fuente unica de verdad).
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Salida informativa: SIEMPRE a stderr (para no contaminar $(...)) ---
info() { printf '\033[36m•\033[0m %s\n' "$*" >&2; }
ok()   { printf '\033[32m✓\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[33m!\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Falta el comando '$1' en el PATH."
}

# Path del config per-proyecto (centralizado: escritor y lector coinciden).
tunnel_config_file() {
    local name="${1:-$TUNNEL_NAME}"
    echo "${CLOUDFLARED_CONFIG_DIR}/${name}.yml"
}

# Guard: prohibe escribir en el config.yml GLOBAL de cloudflared.
assert_cf_config_safe() {
    local path="$1"
    path="${path/#\~/$HOME}"
    local parent filename
    parent="$(cd "$(dirname "${path}")" 2>/dev/null && pwd)" || parent="$(dirname "${path}")"
    filename="$(basename "${path}")"
    local normalized="${parent}/${filename}"
    if [[ "${normalized}" == "${CLOUDFLARED_CONFIG_DIR}/config.yml" || \
          "${normalized}" == "${CLOUDFLARED_CONFIG_DIR}/config.yaml" ]]; then
        die "Prohibido escribir en ${path}: es el config por defecto de cloudflared. Usa ${CLOUDFLARED_CONFIG_DIR}/${TUNNEL_NAME}.yml"
    fi
}

# UUID del tunel por nombre EXACTO (columna, no substring). Nunca del output de create.
get_tunnel_uuid() {
    cloudflared tunnel list 2>/dev/null \
        | awk -v name="${TUNNEL_NAME}" '$2 == name { print $1 }'
}

# Hostnames que enruta este tunel (aqui, uno solo).
tunnel_hostnames() {
    echo "${TUNNEL_HOSTNAME}"
}

# Puerto local del Provider leido de config.yml (fuente unica de verdad).
project_port() {
    local port
    port="$(awk -F: '/^port:/ { gsub(/[^0-9]/, "", $2); print $2; exit }' \
        "${PROJECT_DIR}/config.yml" 2>/dev/null)"
    echo "${port:-8010}"
}

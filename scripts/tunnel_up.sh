#!/usr/bin/env bash
# tunnel_up.sh — Levanta el tunel Cloudflare en foreground (dia a dia).
# Pre-checks + exec con --config explicito. Ctrl+C para detener.
#
# Uso: ./scripts/tunnel_up.sh [--help]

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[[ "${1:-}" == "--help" ]] && { grep '^# ' "$0" | sed 's/^# //'; exit 0; }

require_cmd cloudflared

# Pre-checks: no arrancar un cloudflared sin tunel/config detras.
uuid="$(get_tunnel_uuid)"
[[ -n "${uuid}" ]] || die "Tunel ${TUNNEL_NAME} no existe. Ejecuta: make tunnel-init"
[[ -f "${CLOUDFLARED_CONFIG_FILE}" ]] || die "No existe ${CLOUDFLARED_CONFIG_FILE}. Ejecuta: make tunnel-init"

info "Levantando ${TUNNEL_NAME} (${uuid}) via protocolo ${TUNNEL_PROTOCOL}..."
info "URL publica: https://$(tunnel_hostnames | head -1)"

# exec: el proceso bash se reemplaza; Ctrl+C llega directo a cloudflared.
exec cloudflared tunnel \
    --config "${CLOUDFLARED_CONFIG_FILE}" \
    --protocol "${TUNNEL_PROTOCOL}" \
    run "${TUNNEL_NAME}"

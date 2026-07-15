#!/usr/bin/env bash
# check_dns.sh — Tripwire operativo del tunel: CNAME, endpoint HTTP y proceso.
# Exit 0 si todo OK, 1 si hay problemas.
#
# Uso: ./scripts/check_dns.sh [--help]

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[[ "${1:-}" == "--help" ]] && { grep '^# ' "$0" | sed 's/^# //'; exit 0; }

problems=0
hostname="$(tunnel_hostnames | head -1)"

# 1. Resolucion DNS. Un CNAME proxied por Cloudflare se aplana: dig CNAME
#    devuelve vacio y el hostname resuelve a IPs de Cloudflare via A record.
if command -v dig >/dev/null 2>&1; then
    cname="$(dig +short CNAME "${hostname}" 2>/dev/null || true)"
    a_rec="$(dig +short A "${hostname}" 2>/dev/null | head -1 || true)"
    if [[ "${cname}" == *cfargotunnel.com* ]]; then
        ok "CNAME ${hostname} -> ${cname} (DNS only)"
    elif [[ -n "${a_rec}" ]]; then
        ok "${hostname} -> ${a_rec} (CNAME proxied/aplanado por Cloudflare)"
    else
        warn "${hostname} no resuelve (ni CNAME ni A)."
        problems=1
    fi
else
    warn "dig no disponible; salto verificacion DNS."
fi

# 2. Endpoint HTTP: /health debe devolver 200 (tunel + backend vivos).
code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 \
    -A "moderation-check/1.0" "https://${hostname}/health" 2>/dev/null || echo 000)"
case "${code}" in
    200|404|405) ok "HTTP ${code} en https://${hostname}/health (tunel activo)";;
    522)         warn "HTTP 522: tunel vivo pero backend caido (revisa el server)"; problems=1;;
    530)         warn "HTTP 530: cloudflared no corre (make tunnel-up)"; problems=1;;
    1003)        warn "HTTP 1003: CNAME apunta a otro tunel"; problems=1;;
    000)         warn "Sin respuesta HTTP de https://${hostname}"; problems=1;;
    *)           warn "HTTP ${code} inesperado en https://${hostname}/health"; problems=1;;
esac

# 3. Proceso cloudflared del tunel vivo.
if pgrep -f "cloudflared.*${TUNNEL_NAME}" >/dev/null 2>&1; then
    ok "Proceso cloudflared (${TUNNEL_NAME}) vivo."
else
    warn "No hay proceso cloudflared para ${TUNNEL_NAME} (make tunnel-up)."
    problems=1
fi

# 4. Backend local escuchando.
port="$(project_port)"
if curl -s -o /dev/null --max-time 3 "http://127.0.0.1:${port}/health" 2>/dev/null; then
    ok "Backend local respondiendo en 127.0.0.1:${port}"
else
    warn "Backend local NO responde en 127.0.0.1:${port} (arranca server.py)."
    problems=1
fi

[[ "${problems}" -eq 0 ]] && { ok "Todo OK."; exit 0; } || { die "Hay problemas (ver arriba)."; }

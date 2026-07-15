#!/usr/bin/env bash
# tunnel_init.sh — Bootstrap idempotente del tunel Cloudflare (una sola vez).
# Instala/verifica cloudflared, autentica, crea el tunel, enruta el DNS y
# escribe el config per-proyecto con todas las guardas del estandar.
#
# Uso: ./scripts/tunnel_init.sh [--help]

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[[ "${1:-}" == "--help" ]] && { grep '^# ' "$0" | sed 's/^# //'; exit 0; }

require_cmd cloudflared
require_cmd awk

# 1. Guard global contra escritura al config por defecto.
assert_cf_config_safe "${CLOUDFLARED_CONFIG_FILE}"

# 2. Login (idempotente): cert.pem compartido por cuenta Cloudflare.
if [[ ! -f "${CLOUDFLARED_CONFIG_DIR}/cert.pem" ]]; then
    info "No hay cert.pem; abriendo login de Cloudflare..."
    cloudflared tunnel login >&2
fi
ok "Autenticado (cert.pem presente)."

# 3. Crear el tunel (idempotente). create imprime a stdout -> redirigir a stderr.
if [[ -z "$(get_tunnel_uuid)" ]]; then
    info "Creando tunel ${TUNNEL_NAME}..."
    cloudflared tunnel create "${TUNNEL_NAME}" >&2
fi
uuid="$(get_tunnel_uuid)"
[[ -n "${uuid}" ]] || die "No se pudo obtener el UUID del tunel ${TUNNEL_NAME}."
ok "Tunel ${TUNNEL_NAME} -> ${uuid}"

# 4. Rutas DNS (idempotente con --overwrite-dns).
while IFS= read -r hostname; do
    [[ -z "${hostname}" ]] && continue
    info "Enrutando DNS: ${hostname}"
    cloudflared tunnel route dns --overwrite-dns "${TUNNEL_NAME}" "${hostname}" >&2 \
        || die "Fallo al crear ruta DNS para ${hostname}"
    ok "DNS: ${hostname} -> ${TUNNEL_NAME}"
done < <(tunnel_hostnames)

# 5. Backup del config anterior si existe.
if [[ -f "${CLOUDFLARED_CONFIG_FILE}" ]]; then
    backup="${CLOUDFLARED_CONFIG_FILE}.$(date +%Y%m%d-%H%M%S).bak"
    cp "${CLOUDFLARED_CONFIG_FILE}" "${backup}"
    warn "Backup del config anterior: ${backup}"
fi

# 6. Escribir el config per-proyecto (guard local antes del redirect).
assert_cf_config_safe "${CLOUDFLARED_CONFIG_FILE}"
port="$(project_port)"
{
    echo "tunnel: ${TUNNEL_NAME}"
    echo "credentials-file: ${CLOUDFLARED_CONFIG_DIR}/${uuid}.json"
    echo ""
    echo "ingress:"
    while IFS= read -r hostname; do
        [[ -z "${hostname}" ]] && continue
        echo "  - hostname: ${hostname}"
        echo "    service: http://localhost:${port}"
        echo "    originRequest:"
        echo "      noTLSVerify: true"
        echo "      connectTimeout: 30s"
    done < <(tunnel_hostnames)
    echo "  - service: http_status:404"
} > "${CLOUDFLARED_CONFIG_FILE}"
ok "Config escrito: ${CLOUDFLARED_CONFIG_FILE} (puerto ${port})"

# 7. Validar el ingress; fallar rapido si el YAML esta mal.
if cloudflared tunnel --config "${CLOUDFLARED_CONFIG_FILE}" ingress validate >/dev/null 2>&1; then
    ok "Config YAML validado por cloudflared."
else
    cloudflared tunnel --config "${CLOUDFLARED_CONFIG_FILE}" ingress validate >&2 || true
    die "El YAML no paso la validacion. Corrige ${CLOUDFLARED_CONFIG_FILE}."
fi

ok "Bootstrap completo. Levanta el tunel con: make tunnel-up"

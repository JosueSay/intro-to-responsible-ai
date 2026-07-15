# Túnel Cloudflare

Exposición pública del Provider vía Cloudflare Tunnel, además de la LAN. Sigue
el estándar interno `cloudflare-tunnel-standards` (doble interfaz script +
Makefile, config per-túnel, guardas defensivas).

## Datos del túnel

| Propiedad     | Valor                                          |
| ------------- | ---------------------------------------------- |
| Nombre        | `moderation-dev`                               |
| URL pública   | [dev-moderation.josuesay.com](https://dev-moderation.josuesay.com) |
| Origen        | `http://localhost:8010`                        |
| Config        | `~/.cloudflared/moderation-dev.yml`            |
| Protocolo     | `http2` (QUIC falla en esta versión de cloudflared). |

## Comandos

| Comando            | Script                     | Qué hace                                  |
| ------------------ | -------------------------- | ----------------------------------------- |
| `make tunnel-init` | `scripts/tunnel_init.sh`   | Bootstrap idempotente: crea túnel, ruta DNS y config. |
| `make tunnel-up`   | `scripts/tunnel_up.sh`     | Levanta el túnel en foreground (Ctrl+C para parar). |
| `make dns-check`   | `scripts/check_dns.sh`     | Tripwire: DNS + `/health` + proceso + backend. |

La lógica compartida vive en `scripts/lib.sh`.

## Uso desde un compañero

```bash
python client.py --url https://dev-moderation.josuesay.com --text "hola"
```

## Detalles específicos de esta máquina

- **`--protocol http2`**: la versión instalada de `cloudflared` falla al negociar
  QUIC (`CRYPTO_ERROR 0x178 ... no application protocol`). `tunnel_up.sh` fuerza
  http2. Ver la tabla de troubleshooting del estándar.
- **User-Agent en el cliente**: Cloudflare responde `403` al User-Agent por
  defecto de urllib (`Python-urllib/x.y`); por eso `client.py` envía un UA propio.

## Naming

El túnel se llama `moderation-dev` (nombre del servicio) por ser descriptivo, en
vez del repo-slug estricto `responsible-ai-dev`. Cumple kebab-case + sufijo
`-dev`, y el subdominio sigue el patrón `dev-<service>`.

## Códigos de Cloudflare útiles

| Código | Significado                                   |
| ------ | --------------------------------------------- |
| 200    | Túnel activo y backend respondiendo.          |
| 522    | Túnel vivo pero backend caído (server abajo). |
| 530    | `cloudflared` no está corriendo.              |
| 1003   | El CNAME apunta a otro túnel.                  |

# Servicio de Moderación de Contenido

Laboratorio individual: un **Provider** (API REST `POST /moderate`) y un
**Consumer** (CLI) que consume el endpoint de cualquier compañero.

Solo usa la **librería estándar de Python** (no requiere instalar nada).
PyYAML es opcional: si no está, hay un mini-parser de YAML incluido.

> Documentación desglosada en [docs/](docs/README.md): arquitectura, contrato de
> API, librerías, ejecución, módulos y túnel.

## Archivos

| Archivo         | Rol                                                       |
| --------------- | --------------------------------------------------------- |
| `server.py`     | Provider: API REST con el estándar del lab (200/400/500). |
| `client.py`     | Consumer: CLI que hace el POST y muestra verdict/reason.  |
| `moderation.py` | Lógica de reglas/keywords + carga de `config.yml`.        |
| `config.yml`    | **Toda** la configuración controlable (nada hardcodeado). |

## Estándar (no negociable)

- `POST /moderate` sobre HTTP/JSON, `Content-Type: application/json`.
- Request: `{ "text": "string" }`
- `200`: `{ "verdict": "allowed"|"blocked", "confidence": 0.87, "reason": "..." }`
- `400`: `{ "error": "text is required" }` (text vacío/falta)
- `500`: `{ "error": "string" }` (fallo interno)
- Timeout del cliente: 5s.

## Configuración (`config.yml`)

Todo lo ajustable vive aquí; el código no tiene valores mágicos:

```yaml
host: "0.0.0.0"          # el server escucha en toda la red (no localhost)
port: 8010               # cambiar si el puerto está ocupado
client_timeout: 5        # timeout del cliente en segundos

moderation:
  base_confidence: 0.6         # confianza con 1 coincidencia
  confidence_per_match: 0.1    # +confianza por cada keyword extra
  max_confidence: 0.99         # tope para 'blocked'
  allowed_confidence: 0.95     # confianza cuando se permite
  case_sensitive: false        # ignora mayúsculas/acentos

blocked_keywords:              # reglas de bloqueo
  - idiota
  - odio
  - ...
```

## Correr el servidor (Provider)

```bash
.venv/bin/python server.py
```

Salida esperada:

```text
Servidor escuchando en 0.0.0.0:8010
Reglas cargadas: 17 keywords bloqueadas
[POST /moderate] 192.168.1.10 -> 200 {"verdict":"blocked","confidence":0.7,"reason":"..."}
```

## Usar el cliente (Consumer)

Formato del lab (host/port como parámetros, **nunca** hardcodeados):

```bash
.venv/bin/python client.py host 192.168.1.23 port 8010 text "mensaje a moderar"
```

También acepta banderas y URL directa (útil para el túnel):

```bash
.venv/bin/python client.py --host 192.168.1.23 --port 8010 --text "..."
.venv/bin/python client.py --url https://dev-moderation.josuesay.com --text "..."
.venv/bin/python client.py --host X --port Y --text "..." --timeout 3
```

Salida:

```text
Verdict: BLOCKED | Confidence: 0.87 | Reason: ...
```

Manejo de fallas:

```text
Error: text is required                 # 400
Error del servidor: <msg>               # 500
Provider no disponible (timeout)        # timeout / inalcanzable
```

## Probar rápido (misma máquina)

```bash
# En una terminal:
.venv/bin/python server.py
# En otra:
.venv/bin/python client.py host 127.0.0.1 port 8010 text "eres un idiota"
```

## Exponer por túnel Cloudflare (opcional)

Además de la LAN, el server queda accesible públicamente vía Cloudflare Tunnel,
siguiendo el estándar `cloudflare-tunnel-standards` (doble interfaz script +
Makefile, guardas defensivas, config per-túnel).

- URL pública: **[dev-moderation.josuesay.com](https://dev-moderation.josuesay.com)** → `http://localhost:8010`
- Túnel: `moderation-dev` · config: `~/.cloudflared/moderation-dev.yml`

Operación (interfaz `make`, la lógica vive en `scripts/`):

```bash
make tunnel-init   # bootstrap idempotente (una sola vez): crea túnel, DNS, config
make tunnel-up     # levanta el túnel en foreground (Ctrl+C para detener)
make dns-check     # tripwire: DNS + endpoint /health + proceso + backend
```

Detalles de esta máquina (codificados en los scripts):

- **`--protocol http2`**: QUIC falla en esta versión de `cloudflared`
  (`CRYPTO_ERROR 0x178`). `tunnel_up.sh` fuerza http2.
- El **cliente manda un `User-Agent` propio**: Cloudflare bloquea con `403`
  el User-Agent por defecto de urllib (`Python-urllib/x.y`).

Un compañero consume tu servicio con:

```bash
python client.py --url https://dev-moderation.josuesay.com --text "hola"
```

> Nota de naming: el túnel se llama `moderation-dev` (nombre del servicio) en vez
> de `responsible-ai-dev` (repo-slug estricto), por ser más descriptivo. Cumple
> kebab-case + sufijo `-dev`; el subdominio sigue `dev-<service>`.

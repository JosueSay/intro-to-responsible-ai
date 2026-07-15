# Ejecución: dónde corre y comandos

Desglose de requisitos, puertos y todos los comandos para levantar y probar el
servicio.

## Requisitos

| Requisito | Detalle                                  |
| --------- | ---------------------------------------- |
| Python    | 3.12, disponible en `.venv/bin/python`.  |
| Red       | Provider y Consumer en la misma red LAN (o vía túnel). |
| Puerto    | `8010` por defecto (configurable en `config.yml`). |

> El puerto por defecto es **8010** y no 8000 porque el 8000 y el 8080 ya
> estaban ocupados por otros servicios en esta máquina. Se cambia en `config.yml`.

## Dónde corre cada cosa

| Proceso    | Dirección de escucha | Origen del valor           |
| ---------- | -------------------- | -------------------------- |
| `server.py`| `0.0.0.0:8010`       | `host` y `port` de `config.yml`. |
| `client.py`| N/A (proceso corto)  | Destino por parámetro `host`/`port` o `--url`. |
| Túnel CF   | `localhost:8010` → público | `~/.cloudflared/moderation-dev.yml`. |

## Comandos

### 1. Levantar el servidor (Provider)

```bash
.venv/bin/python server.py
# o con Makefile:
make serve
```

Salida esperada:

```text
Servidor escuchando en 0.0.0.0:8010
Reglas cargadas: 17 keywords bloqueadas
[POST /moderate] 192.168.1.10 -> 200 {"verdict":"blocked",...}
```

### 2. Consumir con el cliente (Consumer)

Formato del lab (host/port como parámetros):

```bash
.venv/bin/python client.py host 192.168.1.23 port 8010 text "mensaje a moderar"
```

Formato con banderas / URL directa / timeout:

```bash
.venv/bin/python client.py --host 192.168.1.23 --port 8010 --text "..."
.venv/bin/python client.py --url https://dev-moderation.josuesay.com --text "..."
.venv/bin/python client.py --host X --port Y --text "..." --timeout 3
```

Atajo con Makefile:

```bash
make moderate TEXT="eres un idiota"
make moderate TEXT="hola" HOST=192.168.1.23 PORT=8010
```

### 3. Prueba rápida en la misma máquina

```bash
# Terminal 1
make serve
# Terminal 2
.venv/bin/python client.py host 127.0.0.1 port 8010 text "eres un idiota"
```

## Salida del cliente

Éxito:

```text
Verdict: BLOCKED | Confidence: 0.87 | Reason: ...
```

Fallas (mensajes claros por cada caso):

```text
Error: text is required                 # respuesta 400
Error del servidor: <msg>               # respuesta 500
Provider no disponible (timeout)        # timeout de 5s o host inalcanzable
```

## Comandos del túnel

Ver [tunel-cloudflare.md](tunel-cloudflare.md) para el detalle.

```bash
make tunnel-init   # bootstrap (una sola vez)
make tunnel-up     # levanta el túnel
make dns-check     # diagnóstico
```

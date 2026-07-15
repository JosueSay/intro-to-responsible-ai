# Desglose por módulo

Descripción archivo por archivo del código.

## `server.py` — Provider

Servidor HTTP con la librería estándar (`ThreadingHTTPServer`). Implementa el
contrato de [contrato-api.md](contrato-api.md).

Elementos principales:

| Elemento              | Descripción                                          |
| --------------------- | ---------------------------------------------------- |
| `ModerationHandler`   | Handler HTTP. `do_POST` maneja `/moderate`.          |
| `_send_json()`        | Envía la respuesta JSON y loguea `[POST ...] IP -> code {...}`. |
| `do_POST()`           | Valida Content-Type y `text`; llama a `moderate()`; captura 500. |
| `do_GET()`            | `/health` y `/` devuelven `{status: ok}` (para probar rápido). |
| `main()`              | Lee `CONFIG` y arranca el server en `host:port`.     |

Manejo de códigos:

- **400** si el Content-Type no es JSON, el body no parsea, o `text` falta/vacío.
- **200** con el resultado de `moderate()`.
- **500** en cualquier excepción no controlada (bloque `try/except`).

## `client.py` — Consumer

CLI que hace el POST y formatea el resultado. `IP:puerto` nunca hardcodeado.

| Función        | Descripción                                              |
| -------------- | -------------------------------------------------------- |
| `parse_args()` | Acepta `host X port Y text Z` y `--host/--port/--text/--url/--timeout`. |
| `build_url()`  | Construye la URL destino desde `host`/`port` o `--url`.  |
| `main()`       | Aplica el timeout, hace el POST y traduce 200/400/500/timeout a mensajes. |

Detalles:

- **Timeout** configurable: bandera `--timeout` > `client_timeout` de `config.yml` > 5s.
- Envía `User-Agent: moderation-client/1.0` (Cloudflare bloquea el UA de urllib con 403).
- Distingue `HTTPError` (400/500) de `URLError`/`TimeoutError` (timeout / inalcanzable).

## `moderation.py` — Lógica y config

Carga la configuración y decide el veredicto.

| Función               | Descripción                                            |
| --------------------- | ------------------------------------------------------ |
| `load_config()`       | Lee `config.yml` (PyYAML si existe, si no el mini-parser). |
| `_minimal_yaml_load()`| Parser mínimo: escalares, listas y un nivel anidado.   |
| `_deep_update()`      | Mezcla defaults con lo cargado (recursivo).            |
| `_normalize()`        | minúsculas + sin acentos (si `case_sensitive` es false). |
| `moderate()`          | Devuelve `(verdict, confidence, reason)`.              |

Cálculo de `confidence`: ver [contrato-api.md](contrato-api.md#lógica-de-decisión-confidence).

## `config.yml` — Configuración

Única fuente de verdad de todo lo ajustable. Nada hardcodeado en el código.

| Clave                            | Uso                                        |
| -------------------------------- | ------------------------------------------ |
| `host`                           | Dirección de escucha del server (`0.0.0.0`). |
| `port`                           | Puerto del server (`8010`).                |
| `client_timeout`                 | Timeout del cliente en segundos.           |
| `moderation.base_confidence`     | Confianza con 1 coincidencia.              |
| `moderation.confidence_per_match`| Incremento por keyword adicional.          |
| `moderation.max_confidence`      | Tope de confianza para `blocked`.          |
| `moderation.allowed_confidence`  | Confianza reportada al permitir.           |
| `moderation.case_sensitive`      | Si `false`, ignora mayúsculas/acentos.     |
| `blocked_keywords`               | Lista de palabras que fuerzan `blocked`.   |

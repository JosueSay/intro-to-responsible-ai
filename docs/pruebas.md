# Pruebas

El set de pruebas sigue el estándar interno de testing: **pytest**, patrón AAA,
sufijo `_test.py` y separación `unit` / `integration`. Se ejecuta de forma
aislada en **contenedores** (lo ideal para reproducibilidad).

## Estructura

```text
tests/
  conftest.py                     # fixture base_url (BASE_URL o localhost)
  unit/
    moderation_test.py            # logica pura: moderate() y load_config()
  integration/
    moderate_api_test.py          # contrato HTTP contra el provider vivo
  helpers/
    api.py                        # post_moderate() / get_health() (stdlib)
  fixtures/
    samples.py                    # textos y settings de referencia
```

## Qué cubre

| Suite       | Casos                                                            |
| ----------- | --------------------------------------------------------------- |
| Unit        | allowed sin match, blocked con match, escala de `confidence`, tope en `max_confidence`, ignora mayúsculas/acentos, `case_sensitive`, carga del bloque anidado. |
| Integration | 200 allowed, 200 blocked, `verdict` ∈ {allowed, blocked}, 400 text vacío, 400 campo ausente, 400 Content-Type inválido, 400 JSON inválido, `/health`. |

Total: **15 pruebas**.

## Ejecución en contenedores (recomendada)

Dos servicios en `docker-compose.yml`: `provider` (server vivo con healthcheck)
y `tests` (corre pytest cuando el provider está `healthy`).

```bash
make test-docker
# equivalente:
docker compose up --build --abort-on-container-exit --exit-code-from tests
```

El exit code del comando es el de pytest (0 = todo verde), útil para CI.

| Variable            | Default | Uso                                             |
| ------------------- | ------- | ----------------------------------------------- |
| `PROVIDER_HOST_PORT`| `8000`  | Puerto del host para alcanzar al provider. Cambiar si el 8000 está ocupado: `PROVIDER_HOST_PORT=18000 make test-docker`. |

Comunicación interna: el contenedor `tests` alcanza al provider en
`http://provider:8000` (red de compose), sin depender del puerto del host.

## Ejecución local (sin Docker)

Requiere el server vivo y pytest instalado en el `.venv`:

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python server.py            # en otra terminal
make test                             # BASE_URL apunta a 127.0.0.1:<port>
```

## Imágenes

| Imagen                 | Base               | Contenido                        |
| ---------------------- | ------------------ | -------------------------------- |
| `moderation-provider`  | `python:3.12-slim` | `server.py` + lógica + config.   |
| `moderation-tests`     | `python:3.12-slim` | pytest + lógica + suite.         |

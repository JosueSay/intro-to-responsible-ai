# Arquitectura

El sistema tiene dos ejecutables independientes que se comunican por HTTP/JSON,
más un módulo de lógica compartido y un archivo de configuración.

## Componentes

| Componente      | Tipo        | Responsabilidad                                     |
| --------------- | ----------- | --------------------------------------------------- |
| `server.py`     | Proceso     | Servidor HTTP (`http.server`). Recibe POST, valida y responde. |
| `client.py`     | CLI         | Arma el POST, aplica timeout y formatea la salida.  |
| `moderation.py` | Módulo      | Carga `config.yml` y decide `allowed`/`blocked`.    |
| `config.yml`    | Config      | Host, puerto, timeout, umbrales y keywords.         |

Tanto `server.py` como `client.py` importan `moderation.py`: el server para
moderar, el client solo para leer el timeout desde `config.yml`.

## Flujo de una request

Recorrido de un `POST /moderate` desde el cliente hasta la respuesta.

```mermaid
flowchart LR
    A[client.py] -->|POST /moderate JSON| B[server.py]
    B --> C{text valido?}
    C -->|No| E[400 text is required]
    C -->|Si| D[moderate en moderation.py]
    D --> F{match keyword?}
    F -->|Si| G[200 blocked]
    F -->|No| H[200 allowed]
    B -->|excepcion interna| I[500 error]
```

## Decisiones de diseño

- **Solo stdlib**: el server usa `http.server.ThreadingHTTPServer` y el client
  `urllib`. No requiere instalar dependencias. Ver [librerias.md](librerias.md).
- **Config única fuente de verdad**: ningún valor ajustable está hardcodeado;
  todo vive en `config.yml`. Ver [modulos.md](modulos.md) y la sección de config.
- **Sin acoplar a la red**: `host` y `port` del server, e `IP:puerto` del client,
  son siempre parámetros/config, nunca literales en el código.

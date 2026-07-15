# Librerías y stack

El proyecto corre con **solo la librería estándar de Python**. No requiere
instalar dependencias para funcionar.

## Entorno

| Elemento    | Valor                                             |
| ----------- | ------------------------------------------------- |
| Lenguaje    | Python 3.12 (`.venv/bin/python`)                  |
| Dependencias obligatorias | Ninguna (stdlib).                   |
| Dependencia opcional | PyYAML (si está, se usa; si no, hay fallback). |

## Módulos de la stdlib usados

| Módulo                | Dónde         | Para qué                                    |
| --------------------- | ------------- | ------------------------------------------- |
| `http.server`         | `server.py`   | `ThreadingHTTPServer` + handler del POST.   |
| `json`                | ambos         | Serializar/parsear el cuerpo JSON.          |
| `urllib.request`      | `client.py`   | Hacer el POST con timeout.                   |
| `urllib.error`        | `client.py`   | Distinguir 400/500 (`HTTPError`) de timeout (`URLError`). |
| `unicodedata`         | `moderation.py` | Normalizar acentos al comparar keywords.  |
| `os`, `sys`           | varios        | Rutas y códigos de salida.                  |

## PyYAML (opcional)

`moderation.py` intenta `import yaml` para leer `config.yml`. Si PyYAML **no**
está instalado (caso del `.venv` actual), usa un **mini-parser incluido**
(`_minimal_yaml_load`) que soporta lo que este `config.yml` necesita: escalares,
listas (`- item`) y un nivel de mapeo anidado (`moderation:`).

Instalar PyYAML es opcional y no cambia el comportamiento:

```bash
.venv/bin/pip install pyyaml
```

## Por qué solo stdlib

- Portabilidad: cualquier compañero puede correrlo sin `pip install`.
- Menos superficie de fallo en la prueba en clase.
- Cumple el requisito del lab sin frameworks (no se requiere ML ni servidores externos).

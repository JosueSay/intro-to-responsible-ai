# Contrato de API

Estándar de comunicación **no negociable** del laboratorio. Todos los
compañeros implementan exactamente este contrato para poder consumirse entre sí.

## Endpoint

| Propiedad     | Valor                                  |
| ------------- | -------------------------------------- |
| Método        | `POST`                                 |
| Ruta          | `/moderate`                            |
| Transporte    | HTTP/JSON                              |
| Content-Type  | `application/json` (obligatorio)       |
| Bind          | `0.0.0.0` (no `localhost`)             |
| Timeout       | 5 s (lo aplica el cliente)             |

## Request

```json
{ "text": "string" }
```

| Campo  | Tipo   | Requerido | Notas                          |
| ------ | ------ | --------- | ------------------------------ |
| `text` | string | Sí        | No puede ser vacío ni faltar.  |

## Respuestas

### 200 OK

```json
{ "verdict": "allowed", "confidence": 0.87, "reason": "string" }
```

| Campo        | Tipo   | Valores / rango                       |
| ------------ | ------ | ------------------------------------- |
| `verdict`    | string | Exactamente `"allowed"` o `"blocked"`. |
| `confidence` | float  | `0.0` – `1.0`.                        |
| `reason`     | string | Explicación legible de la decisión.   |

### 400 Bad Request

Se devuelve cuando `text` falta, es vacío o el `Content-Type` no es JSON.

```json
{ "error": "text is required" }
```

### 500 Internal Server Error

Cualquier fallo interno no controlado.

```json
{ "error": "string" }
```

## Tabla de códigos

| Código | Cuándo                                             | Cuerpo                              |
| ------ | -------------------------------------------------- | ----------------------------------- |
| 200    | Moderación exitosa.                                | `{ verdict, confidence, reason }`   |
| 400    | `text` vacío/ausente o Content-Type no JSON.       | `{ "error": "text is required" }`   |
| 500    | Excepción interna del servidor.                    | `{ "error": "<msg>" }`              |

## Ejemplos con `curl`

Contenido permitido:

```bash
curl -X POST http://192.168.1.23:8010/moderate \
  -H "Content-Type: application/json" \
  -d '{"text":"buenos dias equipo"}'
# {"verdict": "allowed", "confidence": 0.95, "reason": "Sin coincidencias..."}
```

Contenido bloqueado:

```bash
curl -X POST http://192.168.1.23:8010/moderate \
  -H "Content-Type: application/json" \
  -d '{"text":"eres un idiota"}'
# {"verdict": "blocked", "confidence": 0.7, "reason": "Contenido bloqueado..."}
```

Error 400:

```bash
curl -X POST http://192.168.1.23:8010/moderate \
  -H "Content-Type: application/json" \
  -d '{}'
# {"error": "text is required"}
```

## Lógica de decisión (`confidence`)

El veredicto y la confianza se calculan en `moderation.py` a partir de los
umbrales de `config.yml`:

- **Sin coincidencias** → `allowed`, `confidence = allowed_confidence` (0.95).
- **Con N coincidencias** → `blocked`,
  `confidence = min(max_confidence, base_confidence + confidence_per_match * N)`.

Ver el desglose en [modulos.md](modulos.md).

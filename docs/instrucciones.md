# Laboratorio: Servicio de Moderación de Contenido

Trabajo individual. Sin parejas ni roles fijos: cada quien construye la misma aplicación, que expone un endpoint de moderación y consume el de cualquier compañero. Pruebas entre computadoras, misma red (hotspot en parejas solo para probar antes; el lab se califica individual en clase).

## Estándar de comunicación (fijo, no negociable)

**POST** `/moderate` sobre **HTTP/JSON**.

- `Content-Type: application/json` obligatorio.
- `confidence` es `float` `0.0–1.0`.
- `verdict` es exactamente `"allowed"` o `"blocked"`.
- Timeout: **5 s**.

### Request

```json
{
  "text": "string"
}
```

### Respuestas

**200 OK**

```json
{
  "verdict": "allowed|blocked",
  "confidence": 0.87,
  "reason": "string"
}
```

**400**

```json
{
  "error": "text is required"
}
```

> (text vacío/falta)

**500**

```json
{
  "error": "string"
}
```

> (fallo interno)

## Instrucciones

### Servidor (Provider)

- API REST con el estándar exacto de arriba.
- Clasificación por reglas/keywords (no se requiere ML).
- Correr en `0.0.0.0` (no `localhost`).
- Implementar respuestas `200/400/500`.

### Cliente (Consumer)

- CLI que recibe texto + IP:puerto destino.
- Hace el `POST`.
- Muestra `verdict` y `reason`.
- Maneja `200/400/500` y timeout de **5 s** con mensaje claro.
- IP:puerto como parámetro, nunca hardcodeado.

Su app debe:

1. Recibir moderación de cualquier compañero.
2. Atender a cualquier compañero.

## Ejemplo de output

```text
Servidor:  Servidor escuchando en 0.0.0.0:8000
[POST /moderate] 192.168.1.10 -> 200 {"verdict":"blocked","confidence":0.87,"reason":"..."}

Cliente:  $ python client.py --host 192.168.1.23 --port 8000 --text "..."
Verdict: BLOCKED | Confidence: 0.87 | Reason: ...

Fallas: Error: text is required / Error del servidor: <msg> / Provider no disponible (timeout)
```

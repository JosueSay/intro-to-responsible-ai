Laboratorio: Servicio de Moderación de Contenido
Trabajo individual. Sin parejas ni roles jos: cada quien construye la misma aplicación, que expone un endpoint de
moderación y consume el de cualquier compañero. Pruebas entre computadoras, misma red (hotspot en parejas solo para
probar antes; el lab se calica individual en clase).
Estándar de comunicación (jo, no negociable)
POST /moderate sobre HTTP/JSON. Content-Type: application/json obligatorio. condence es oat 0.01.0. verdict
es exactamente "allowed" o "blocked" . Timeout: 5s.
Request: { "text": "string" }
200 OK: { "verdict": "allowed"|"blocked", "confidence": 0.87, "reason": "string" }
400: { "error": "text is required" } (text vacío/falta)
500: { "error": "string" } (fallo interno)
Instrucciones
Servidor (Provider): API REST con el estándar exacto de arriba. Clasicación por reglas/keywords (no se requiere
ML). Correr en 0.0.0.0 (no localhost ). Implementar 200/400/500.
Cliente (Consumer): CLI que recibe texto + IP:puerto destino, hace el POST , muestra verdict y reason . Maneja
200/400/500 y timeout de 5s con mensaje claro. IP:puerto como parámetro, nunca hardcodeado.
Su app debe: (a) recibir moderación de cualquier compañero, y (b) atender a cualquier compañero.
Ejemplo de output
Servidor: Servidor escuchando en 0.0.0.0:8000
[POST /moderate] 192.168.1.10 -> 200 {"verdict":"blocked","confidence":0.87,"reason":"..."}
Cliente: $ python client.py host 192.168.1.23 port 8000 text "..."
Verdict: BLOCKED | Confidence: 0.87 | Reason: ...
Fallas: Error: text is required / Error del servidor: <msg> / Provider no disponible (timeout)

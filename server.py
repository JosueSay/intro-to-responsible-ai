"""Provider: API REST de moderación de contenido.

Estándar (no negociable):
  POST /moderate  Content-Type: application/json
  Request : { "text": "string" }
  200 OK  : { "verdict": "allowed"|"blocked", "confidence": 0.87, "reason": "..." }
  400     : { "error": "text is required" }        (text vacío/falta)
  500     : { "error": "string" }                  (fallo interno)

Corre en 0.0.0.0 (accesible en la red, no localhost). Solo stdlib.
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from moderation import load_config, moderate

CONFIG = load_config()


class ModerationHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)
        # log estilo: [POST /moderate] 192.168.1.10 -> 200 {...}
        client_ip = self.client_address[0]
        print(f"[{self.command} {self.path}] {client_ip} -> {status} "
              f"{json.dumps(payload, ensure_ascii=False)}", flush=True)

    def do_POST(self):
        if self.path != "/moderate":
            self._send_json(404, {"error": "not found"})
            return
        try:
            ctype = self.headers.get("Content-Type", "")
            if "application/json" not in ctype.lower():
                self._send_json(400, {"error": "Content-Type must be application/json"})
                return

            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length > 0 else b""

            try:
                data = json.loads(raw.decode("utf-8")) if raw else {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"error": "invalid JSON body"})
                return

            text = data.get("text") if isinstance(data, dict) else None
            if not isinstance(text, str) or text.strip() == "":
                self._send_json(400, {"error": "text is required"})
                return

            verdict, confidence, reason = moderate(
                text, CONFIG["blocked_keywords"], CONFIG.get("moderation"))
            self._send_json(200, {
                "verdict": verdict,
                "confidence": confidence,
                "reason": reason,
            })
        except Exception as exc:  # cualquier fallo interno -> 500
            self._send_json(500, {"error": f"internal error: {exc}"})

    def do_GET(self):
        # Endpoint de salud opcional para probar rápido en el navegador.
        if self.path in ("/", "/health"):
            self._send_json(200, {"status": "ok", "service": "moderation"})
        elif self.path == "/moderate":
            # /moderate existe pero solo por POST -> 405, no 404.
            self._send_json(405, {"error": "method not allowed, use POST"},
                            extra_headers={"Allow": "POST"})
        else:
            self._send_json(404, {"error": "not found"})

    def _reject_method(self):
        """Métodos no soportados (PUT/DELETE/PATCH) -> 405 en /moderate, 404 resto."""
        if self.path == "/moderate":
            self._send_json(405, {"error": "method not allowed, use POST"},
                            extra_headers={"Allow": "POST"})
        else:
            self._send_json(404, {"error": "not found"})

    do_PUT = _reject_method
    do_DELETE = _reject_method
    do_PATCH = _reject_method

    def log_message(self, *args):
        pass  # silenciamos el log por defecto; usamos el nuestro


def main():
    host = CONFIG["host"]
    port = int(CONFIG["port"])
    server = ThreadingHTTPServer((host, port), ModerationHandler)
    print(f"Servidor escuchando en {host}:{port}", flush=True)
    print(f"Reglas cargadas: {len(CONFIG['blocked_keywords'])} keywords bloqueadas",
          flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
        server.server_close()


if __name__ == "__main__":
    main()

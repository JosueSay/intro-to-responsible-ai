"""Consumer: CLI que consume el endpoint /moderate de cualquier compañero.

Uso (con guiones, forma recomendada):
  python client.py --host 192.168.1.23 --port 8000 --text "mensaje a moderar"
  python client.py --url https://algo.trycloudflare.com --text "mensaje"

También acepta el formato posicional del enunciado:
  python client.py host 192.168.1.23 port 8000 text "mensaje"

IP:puerto SIEMPRE por parámetro, nunca hardcodeado. Timeout de 5s.
"""

import json
import sys
import urllib.error
import urllib.request

from moderation import load_config


def parse_args(argv):
    """Soporta '--host X --port Y --text Z' (con guiones) y también el formato
    posicional 'host X port Y text Z', más '--url' y '--timeout'."""
    args = {}
    i = 0
    tokens = argv[:]
    while i < len(tokens):
        key = tokens[i].lstrip("-").lower()
        if key in ("host", "port", "text", "url", "timeout") and i + 1 < len(tokens):
            args[key] = tokens[i + 1]
            i += 2
        else:
            i += 1
    return args


def build_url(args):
    if "url" in args:
        base = args["url"].rstrip("/")
        return base + "/moderate"
    host = args.get("host")
    port = args.get("port")
    if not host or not port:
        raise ValueError("Faltan parámetros: --host y --port (o --url) son obligatorios.")
    return f"http://{host}:{port}/moderate"


def format_verdict(raw):
    """Normaliza el verdict de forma tolerante: acepta cualquier formato que
    mande el compañero (allowed/ALLOWED/Allow/blocked/BLOCK/...)."""
    v = str(raw).strip().lower()
    if v.startswith("allow"):
        return "ALLOWED"
    if v.startswith("block"):
        return "BLOCKED"
    return str(raw).upper()   # formato desconocido: se muestra tal cual


def describe_http_error(code, msg):
    """Traduce cualquier código HTTP a un mensaje claro para el usuario."""
    if code == 400:
        return f"Error: {msg}"
    if code in (401, 403):
        return f"Error: no autorizado ({code}): {msg}"
    if code == 404:
        return f"Error: endpoint no encontrado ({code}): {msg}"
    if code == 405:
        return f"Error: método no permitido ({code}): {msg}"
    if 400 <= code < 500:
        return f"Error de cliente ({code}): {msg}"
    if 500 <= code < 600:
        # Formato exacto del enunciado: "Error del servidor: <msg>"
        return f"Error del servidor: {msg}"
    return f"Respuesta inesperada ({code}): {msg}"


def main(argv):
    args = parse_args(argv)

    # timeout controlable: bandera --timeout > config.yml (client_timeout) > 5
    config = load_config()
    try:
        timeout = float(args["timeout"]) if "timeout" in args \
            else float(config.get("client_timeout", 5))
    except (ValueError, TypeError):
        timeout = 5.0

    if "text" not in args:
        print("Uso: python client.py --host <IP> --port <PUERTO> --text \"<mensaje>\"")
        print("  o: python client.py --url <URL> --text \"<mensaje>\" [--timeout 5]")
        return 2

    try:
        url = build_url(args)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    payload = json.dumps({"text": args["text"]}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            # UA explícito: algunos proxies/CDN (p.ej. Cloudflare) bloquean
            # el User-Agent por defecto de urllib con 403.
            "User-Agent": "moderation-client/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            # Compañero que no devuelve JSON: mostramos lo que haya.
            print(f"Respuesta no-JSON del provider: {raw.strip()}")
            return 1
        if not isinstance(body, dict):
            print(f"Respuesta inesperada del provider: {body}")
            return 1

        verdict = format_verdict(body.get("verdict", "?"))
        confidence = body.get("confidence", "?")
        reason = body.get("reason", "")
        print(f"Verdict: {verdict} | Confidence: {confidence} | Reason: {reason}")
        return 0

    except urllib.error.HTTPError as exc:
        # El servidor respondió con un código de error; leemos el cuerpo si hay.
        try:
            body = json.loads(exc.read().decode("utf-8"))
            msg = body.get("error", exc.reason) if isinstance(body, dict) else exc.reason
        except Exception:
            msg = exc.reason
        print(describe_http_error(exc.code, msg))
        return 1

    except urllib.error.URLError as exc:
        # timeout, "no route to host", conexión rechazada, DNS, etc.
        reason = getattr(exc, "reason", exc)
        if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
            print("Provider no disponible (timeout)")
        else:
            print(f"Provider no disponible: {reason}")
        return 1

    except TimeoutError:
        print("Provider no disponible (timeout)")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Helpers HTTP para los tests de integracion (solo stdlib)."""

import json
import urllib.error
import urllib.request


def post_moderate(base_url, payload=None, raw=None,
                  content_type="application/json", timeout=5):
    """Hace POST /moderate y devuelve el status y el cuerpo parseado.

    Args:
        base_url: URL base del provider (ej. http://provider:8010).
        payload: dict a serializar como JSON. Se ignora si se pasa `raw`.
        raw: bytes crudos a enviar tal cual (para probar JSON invalido).
        content_type: valor del header Content-Type.
        timeout: timeout en segundos.

    Returns:
        Tupla (status_code, body) donde body es el dict del JSON de respuesta.
    """
    data = raw if raw is not None else json.dumps(payload or {}).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/moderate",
        data=data,
        headers={
            "Content-Type": content_type,
            "User-Agent": "moderation-tests/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        return exc.code, body


def get_health(base_url, timeout=5):
    """Hace GET /health y devuelve el cuerpo parseado."""
    with urllib.request.urlopen(f"{base_url}/health", timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

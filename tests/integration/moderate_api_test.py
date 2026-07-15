"""Pruebas de integracion contra el provider vivo (HTTP/JSON)."""

from tests.fixtures.samples import ALLOWED_TEXT, BLOCKED_TEXT
from tests.helpers.api import get_health, post_moderate


class TestModerateApi:
    """Contrato de POST /moderate: 200 / 400 y forma de la respuesta."""

    def test_200_allowed(self, base_url):
        # Act
        status, body = post_moderate(base_url, {"text": ALLOWED_TEXT})
        # Assert
        assert status == 200
        assert body["verdict"] == "allowed"
        assert 0.0 <= body["confidence"] <= 1.0
        assert "reason" in body

    def test_200_blocked(self, base_url):
        # Act
        status, body = post_moderate(base_url, {"text": BLOCKED_TEXT})
        # Assert
        assert status == 200
        assert body["verdict"] == "blocked"
        assert 0.0 <= body["confidence"] <= 1.0

    def test_verdict_es_solo_allowed_o_blocked(self, base_url):
        # Act
        _, body = post_moderate(base_url, {"text": BLOCKED_TEXT})
        # Assert
        assert body["verdict"] in ("allowed", "blocked")

    def test_400_text_vacio(self, base_url):
        # Act
        status, body = post_moderate(base_url, {"text": ""})
        # Assert
        assert status == 400
        assert body["error"] == "text is required"

    def test_400_campo_ausente(self, base_url):
        # Act
        status, body = post_moderate(base_url, {})
        # Assert
        assert status == 400
        assert body["error"] == "text is required"

    def test_400_content_type_invalido(self, base_url):
        # Act
        status, _ = post_moderate(base_url, {"text": "hola"},
                                  content_type="text/plain")
        # Assert
        assert status == 400

    def test_400_json_invalido(self, base_url):
        # Act
        status, _ = post_moderate(base_url, raw=b"{ esto no es json")
        # Assert
        assert status == 400

    def test_400_text_no_string(self, base_url):
        # Arrange: caso borde no definido en el enunciado -> asumimos 400.
        # Act
        status, body = post_moderate(base_url, {"text": 123})
        # Assert
        assert status == 400
        assert body["error"] == "text is required"

    def test_400_text_solo_espacios(self, base_url):
        # Arrange: text de solo espacios se trata como vacio (strip).
        # Act
        status, body = post_moderate(base_url, {"text": "    "})
        # Assert
        assert status == 400
        assert body["error"] == "text is required"

    def test_reason_presente_en_allowed(self, base_url):
        # Arrange: el enunciado no muestra un allowed; asumimos reason siempre.
        # Act
        _, body = post_moderate(base_url, {"text": "buenos dias"})
        # Assert
        assert body["verdict"] == "allowed"
        assert body.get("reason")


class TestHealth:
    """Endpoint auxiliar de salud."""

    def test_health_ok(self, base_url):
        # Act
        body = get_health(base_url)
        # Assert
        assert body["status"] == "ok"

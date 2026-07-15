"""Pruebas unitarias de la logica de moderacion (sin servidor)."""

from moderation import load_config, moderate
from tests.fixtures.samples import KEYWORDS, SETTINGS


class TestModerate:
    """Comportamiento de la funcion moderate()."""

    def test_allowed_cuando_no_hay_keywords(self):
        # Arrange
        text = "hola buen dia a todos"
        # Act
        verdict, confidence, reason = moderate(text, KEYWORDS, SETTINGS)
        # Assert
        assert verdict == "allowed"
        assert confidence == 0.95
        assert reason

    def test_blocked_con_una_keyword(self):
        # Arrange
        text = "eres un idiota"
        # Act
        verdict, confidence, reason = moderate(text, KEYWORDS, SETTINGS)
        # Assert
        assert verdict == "blocked"
        assert confidence == 0.7          # 0.6 + 0.1 * 1
        assert "idiota" in reason

    def test_confidence_sube_con_mas_coincidencias(self):
        # Arrange
        text = "idiota y mucho odio"
        # Act
        _, confidence, _ = moderate(text, KEYWORDS, SETTINGS)
        # Assert
        assert confidence == 0.8          # 0.6 + 0.1 * 2

    def test_confidence_tope_en_max_confidence(self):
        # Arrange: 5 coincidencias darian 1.1, debe topar en 0.99
        keywords = ["a", "b", "c", "d", "e"]
        # Act
        _, confidence, _ = moderate("a b c d e", keywords, SETTINGS)
        # Assert
        assert confidence == 0.99

    def test_ignora_mayusculas_y_acentos(self):
        # Arrange
        text = "ERES UN IDIOTA"
        # Act
        verdict, _, _ = moderate(text, KEYWORDS, SETTINGS)
        # Assert
        assert verdict == "blocked"

    def test_case_sensitive_no_matchea_mayusculas(self):
        # Arrange
        settings = {**SETTINGS, "case_sensitive": True}
        # Act
        verdict, _, _ = moderate("ERES UN IDIOTA", KEYWORDS, settings)
        # Assert
        assert verdict == "allowed"


class TestLoadConfig:
    """Carga de config.yml (incluye el bloque anidado sin PyYAML)."""

    def test_carga_bloque_moderation_anidado(self):
        # Act
        config = load_config()
        # Assert
        assert config["moderation"]["base_confidence"] == 0.6
        assert config["moderation"]["case_sensitive"] is False
        assert isinstance(config["blocked_keywords"], list)
        assert len(config["blocked_keywords"]) > 0

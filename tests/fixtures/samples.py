"""Textos de ejemplo reutilizables en los tests."""

# Texto sin coincidencias -> allowed.
ALLOWED_TEXT = "buenos dias equipo, que tengan buen laboratorio"

# Texto con una keyword -> blocked.
BLOCKED_TEXT = "eres un idiota"

# Texto con varias keywords -> blocked con mayor confianza.
MULTI_BLOCKED_TEXT = "idiota, te odio, esto es pura violencia"

# Keywords y settings de referencia para los tests unitarios (no dependen
# del config.yml real para no acoplar el test a su contenido).
KEYWORDS = ["idiota", "odio", "violencia"]

SETTINGS = {
    "base_confidence": 0.6,
    "confidence_per_match": 0.1,
    "max_confidence": 0.99,
    "allowed_confidence": 0.95,
    "case_sensitive": False,
}

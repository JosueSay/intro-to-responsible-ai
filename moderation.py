"""Lógica de moderación por reglas/keywords y carga de configuración.

Sin dependencias externas obligatorias: si PyYAML está instalado se usa,
si no, se usa un mini-parser suficiente para este config.yml (escalares,
listas y un nivel de mapeo anidado).
"""

import os
import unicodedata

DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 8010,
    "client_timeout": 5,
    "moderation": {
        "base_confidence": 0.6,
        "confidence_per_match": 0.1,
        "max_confidence": 0.99,
        "allowed_confidence": 0.95,
        "case_sensitive": False,
    },
    "blocked_keywords": [],
}


def _coerce(value):
    """Convierte un escalar de texto a int/float/bool cuando aplica."""
    v = value.strip().strip('"').strip("'")
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _minimal_yaml_load(text):
    """Parser mínimo: escalares top-level, listas (- item) y mapeos anidados
    a un nivel (suficiente para este config.yml). No es YAML completo."""
    root = {}
    current_list = None      # lista activa (para elementos '- item')
    current_map = None       # dict anidado activo (por indentación)

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if stripped.startswith("- "):                 # elemento de lista
            if current_list is not None:
                current_list.append(_coerce(stripped[2:]))
            continue

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if indent == 0:                                # clave top-level
            current_map = None
            if value == "":                            # abre lista o mapa
                current_list = []
                root[key] = current_list               # provisional
                current_map = {}
                root[key + "__map"] = current_map      # provisional alterno
            else:
                current_list = None
                root[key] = _coerce(value)
        else:                                          # clave anidada
            current_list = None
            if current_map is not None:
                current_map[key] = _coerce(value)

    # Resolver claves que abrieron bloque: lista si tuvo items, mapa si no.
    resolved = {}
    for key, val in list(root.items()):
        if key.endswith("__map"):
            continue
        if isinstance(val, list) and not val and (key + "__map") in root:
            resolved[key] = root[key + "__map"] or []
        else:
            resolved[key] = val
    return resolved


def _deep_update(base, overrides):
    for k, v in overrides.items():
        if v is None:
            continue
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_update(base[k], v)
        else:
            base[k] = v
    return base


def load_config(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    config = _deep_update({}, DEFAULT_CONFIG)  # copia profunda simple
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        try:
            import yaml  # opcional
            loaded = yaml.safe_load(text) or {}
        except ImportError:
            loaded = _minimal_yaml_load(text)
        _deep_update(config, loaded)
    except FileNotFoundError:
        pass
    config["blocked_keywords"] = [str(k) for k in config.get("blocked_keywords", [])]
    return config


def _normalize(text, case_sensitive):
    if case_sensitive:
        return text
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def moderate(text, blocked_keywords, settings=None):
    """Devuelve (verdict, confidence, reason).

    settings: dict con base_confidence, confidence_per_match, max_confidence,
    allowed_confidence, case_sensitive. Si falta, usa los defaults.
    """
    s = dict(DEFAULT_CONFIG["moderation"])
    if settings:
        s.update({k: v for k, v in settings.items() if v is not None})

    case_sensitive = bool(s["case_sensitive"])
    norm_text = _normalize(text, case_sensitive)

    matches = [kw for kw in blocked_keywords
               if _normalize(kw, case_sensitive) in norm_text]

    if matches:
        confidence = min(
            s["max_confidence"],
            s["base_confidence"] + s["confidence_per_match"] * len(matches),
        )
        reason = "Contenido bloqueado. Palabras prohibidas: " + ", ".join(matches)
        return "blocked", round(confidence, 2), reason

    return "allowed", round(s["allowed_confidence"], 2), \
        "Sin coincidencias con reglas de contenido prohibido."

"""Fixtures compartidas por los tests."""

import os

import pytest


@pytest.fixture
def base_url():
    """URL base del provider.

    En el contenedor de pruebas se inyecta BASE_URL (http://provider:8010);
    en local cae a 127.0.0.1 con el puerto por defecto.
    """
    return os.environ.get("BASE_URL", "http://127.0.0.1:8010")

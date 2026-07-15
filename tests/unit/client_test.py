"""Pruebas unitarias de los helpers del cliente."""

from client import describe_http_error, format_verdict, parse_args


class TestFormatVerdict:
    """El verdict se muestra tolerante a cualquier formato del compañero."""

    def test_allowed_en_minuscula(self):
        assert format_verdict("allowed") == "ALLOWED"

    def test_blocked_en_mayuscula(self):
        assert format_verdict("BLOCKED") == "BLOCKED"

    def test_variantes_se_normalizan(self):
        # Arrange / Act / Assert
        assert format_verdict("Allow") == "ALLOWED"
        assert format_verdict("block") == "BLOCKED"

    def test_formato_desconocido_se_muestra_tal_cual(self):
        assert format_verdict("desconocido") == "DESCONOCIDO"


class TestDescribeHttpError:
    """Cada familia de códigos HTTP produce un mensaje claro."""

    def test_400(self):
        assert describe_http_error(400, "text is required") == "Error: text is required"

    def test_401_y_403_no_autorizado(self):
        assert "no autorizado (401)" in describe_http_error(401, "x")
        assert "no autorizado (403)" in describe_http_error(403, "x")

    def test_404_endpoint(self):
        assert "no encontrado (404)" in describe_http_error(404, "x")

    def test_5xx_servidor(self):
        # Formato exacto del enunciado (sin el código).
        assert describe_http_error(500, "boom") == "Error del servidor: boom"

    def test_otro_4xx_generico(self):
        assert describe_http_error(422, "x") == "Error de cliente (422): x"


class TestParseArgs:
    """Acepta guiones y formato posicional."""

    def test_con_guiones(self):
        args = parse_args(["--host", "1.2.3.4", "--port", "8000", "--text", "hola"])
        assert args == {"host": "1.2.3.4", "port": "8000", "text": "hola"}

    def test_posicional(self):
        args = parse_args(["host", "1.2.3.4", "port", "8000", "text", "hola"])
        assert args == {"host": "1.2.3.4", "port": "8000", "text": "hola"}

from app.orchestrator.cu01.extractors import regex_extract


class TestCU01ExtractorURL:
    def test_extrae_url_https(self):
        result = regex_extract("Analiza https://paypal-secure.login.com/verify")
        assert result == {"raw_input": "https://paypal-secure.login.com/verify"}

    def test_extrae_url_http(self):
        result = regex_extract("revisa http://evil.tk/phishing")
        assert result == {"raw_input": "http://evil.tk/phishing"}

    def test_url_tiene_prioridad_sobre_dominio(self):
        result = regex_extract("ve a https://ejemplo.com y también ejemplo.com")
        assert result["raw_input"].startswith("https://")


class TestCU01ExtractorEmail:
    def test_extrae_email(self):
        result = regex_extract("el correo es usuario@banco-seguro.com")
        assert result == {"raw_input": "usuario@banco-seguro.com"}

    def test_email_tiene_prioridad_sobre_dominio(self):
        result = regex_extract("usuario@paypal.com es sospechoso")
        assert "@" in result["raw_input"]


class TestCU01ExtractorDominio:
    def test_extrae_dominio_simple(self):
        result = regex_extract("analiza paypal-login.tk")
        assert result == {"raw_input": "paypal-login.tk"}

    def test_sin_input_devuelve_vacio(self):
        result = regex_extract("quiero analizar algo")
        assert result == {}

    def test_mensaje_vacio(self):
        result = regex_extract("")
        assert result == {}

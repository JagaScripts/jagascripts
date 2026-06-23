from app.tools.cu02 import _validate_domain_name


class TestValidateDomainName:
    def test_dominio_valido(self):
        result = _validate_domain_name("prueba.com")
        assert result["valid"] is True
        assert result["issues"] == []

    def test_dominio_con_subdominio(self):
        result = _validate_domain_name("www.prueba.com")
        assert result["valid"] is True

    def test_dominio_con_guion(self):
        result = _validate_domain_name("mi-empresa.com")
        assert result["valid"] is True

    def test_dominio_vacio(self):
        result = _validate_domain_name("")
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_dominio_solo_espacios(self):
        result = _validate_domain_name("   ")
        assert result["valid"] is False

    def test_dominio_sin_tld(self):
        result = _validate_domain_name("solounstring")
        assert result["valid"] is False

    def test_dominio_muy_corto(self):
        result = _validate_domain_name("a.")
        assert result["valid"] is False

    def test_dominio_con_caracteres_invalidos(self):
        result = _validate_domain_name("dominio con espacios.com")
        assert result["valid"] is False

from app.orchestrator.cu04.extractors import extract_question


class TestCU04ExtractQuestion:
    def test_seleccion_menu_04(self):
        assert extract_question("04") is None

    def test_seleccion_menu_4(self):
        assert extract_question("4") is None

    def test_seleccion_base_conocimiento(self):
        assert extract_question("base de conocimiento") is None

    def test_seleccion_rag(self):
        assert extract_question("rag") is None

    def test_pregunta_directa(self):
        result = extract_question("¿Qué es el phishing por subdominios?")
        assert result == "¿Qué es el phishing por subdominios?"

    def test_pregunta_con_prefijo_consultar(self):
        result = extract_question("consultar: cómo detectar dominios falsos")
        assert result == "cómo detectar dominios falsos"

    def test_pregunta_con_prefijo_dime(self):
        result = extract_question("dime qué es el typosquatting")
        assert result == "qué es el typosquatting"

    def test_pregunta_con_prefijo_explica(self):
        result = extract_question("explícame las técnicas de phishing más comunes")
        assert result == "las técnicas de phishing más comunes"

    def test_mensaje_vacio(self):
        assert extract_question("") is None

    def test_pregunta_sin_prefijo(self):
        result = extract_question("técnicas de phishing en correos electrónicos")
        assert result == "técnicas de phishing en correos electrónicos"

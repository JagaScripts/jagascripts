from app.orchestrator.cu02.extractors import regex_extract, extract_crud_intent


class TestCU02RegexExtract:
    def test_extrae_dominio(self):
        result = regex_extract("registra el dominio prueba.com")
        assert result["domain_name"] == "prueba.com"

    def test_extrae_tags_con_coma(self):
        result = regex_extract("prueba.com tags: marca, cliente")
        assert "marca" in result["tags"]
        assert "cliente" in result["tags"]

    def test_extrae_tags_con_etiquetas(self):
        result = regex_extract("etiquetas: fintech, b2b")
        assert result["tags"] == ["fintech", "b2b"]

    def test_sin_tags_keyword(self):
        result = regex_extract("no")
        assert result.get("tags") == []

    def test_sin_tags_keyword_ninguna(self):
        result = regex_extract("ninguna")
        assert result.get("tags") == []

    def test_mensaje_sin_dominio(self):
        result = regex_extract("hola, quiero registrar un dominio")
        assert "domain_name" not in result


class TestCU02CrudIntent:
    def test_intención_listar(self):
        result = extract_crud_intent("ver mis dominios")
        assert result["intent"] == "list"

    def test_intención_listar_alternativa(self):
        result = extract_crud_intent("mostrar dominios registrados")
        assert result["intent"] == "list"

    def test_intención_eliminar_con_dominio(self):
        result = extract_crud_intent("eliminar dominio prueba.com")
        assert result["intent"] == "delete"
        assert result["domain_name"] == "prueba.com"

    def test_intención_desactivar(self):
        result = extract_crud_intent("desactivar prueba.com")
        assert result["intent"] == "update_status"
        assert result["new_status"] == "inactivo"

    def test_intención_activar(self):
        result = extract_crud_intent("activar prueba.com")
        assert result["intent"] == "update_status"
        assert result["new_status"] == "activo"

    def test_intención_actualizar_tags(self):
        result = extract_crud_intent("cambiar tags de prueba.com")
        assert result["intent"] == "update_tags"

    def test_sin_intención(self):
        result = extract_crud_intent("hola, buenos días")
        assert result["intent"] is None

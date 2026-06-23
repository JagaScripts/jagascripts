from app.orchestrator.cu03.extractors import regex_extract, extract_cu03_crud_intent


class TestCU03RegexExtract:
    def test_extrae_nombre_con_comillas(self):
        result = regex_extract("llámala 'Alerta Paypal'")
        assert result["rule_name"] == "Alerta Paypal"

    def test_extrae_nombre_con_comillas_dobles(self):
        result = regex_extract('nombre: "Vigilancia dominio"')
        assert result["rule_name"] == "Vigilancia dominio"

    def test_extrae_email_como_canal(self):
        result = regex_extract("notifícame en admin@empresa.com")
        assert result["channels"][0]["kind"] == "email"
        assert result["channels"][0]["to"] == "admin@empresa.com"

    def test_extrae_dominio_como_scope(self):
        result = regex_extract("para el dominio prueba.com")
        assert "prueba.com" in result["scope"]["domains"]

    def test_extrae_dias_caducidad(self):
        result = regex_extract("avísame 30 días antes de que caduque")
        assert result["condition"] == {"days_before_expiry": 30}

    def test_extrae_frecuencia_diaria(self):
        result = regex_extract("revísalo diariamente")
        assert result["schedule"]["frequency"] == "daily"

    def test_extrae_frecuencia_semanal(self):
        result = regex_extract("quiero alertas semanales")
        assert result["schedule"]["frequency"] == "weekly"

    def test_extrae_hora(self):
        result = regex_extract("envíalo a las 08:00")
        assert result["schedule"]["at_time"] == "08:00"

    def test_condicion_riesgo_alto(self):
        result = regex_extract("cuando haya riesgo alto")
        assert result["condition"] == {"risk_level": "high"}

    def test_sin_cooldown(self):
        result = regex_extract("sin cooldown por favor")
        assert result["cooldown"] == {"seconds": 0}

    def test_mensaje_sin_datos(self):
        result = regex_extract("quiero crear una alerta")
        assert result == {}


class TestCU03CrudIntent:
    def test_intención_listar(self):
        result = extract_cu03_crud_intent("ver mis alertas")
        assert result["intent"] == "list"

    def test_intención_listar_alternativa(self):
        result = extract_cu03_crud_intent("mostrar alertas activas")
        assert result["intent"] == "list"

    def test_intención_eliminar(self):
        result = extract_cu03_crud_intent("eliminar alerta 'Vigilancia Paypal'")
        assert result["intent"] == "delete"
        assert result["rule_name"] == "vigilancia paypal"

    def test_intención_pausar(self):
        result = extract_cu03_crud_intent("pausar alerta 'Mi Alerta'")
        assert result["intent"] == "pause"
        assert result["rule_name"] == "mi alerta"

    def test_intención_activar(self):
        result = extract_cu03_crud_intent("activar regla 'Monitor Diario'")
        assert result["intent"] == "enable"
        assert result["rule_name"] == "monitor diario"

    def test_standalone_eliminar(self):
        result = extract_cu03_crud_intent("eliminar")
        assert result["intent"] == "delete"

    def test_standalone_pausar(self):
        result = extract_cu03_crud_intent("pausar")
        assert result["intent"] == "pause"

    def test_sin_intención(self):
        result = extract_cu03_crud_intent("hola, buenos días")
        assert result["intent"] is None

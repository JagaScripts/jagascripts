from datetime import datetime, timezone, timedelta
from app.orchestrator.cu02.extractors import extract_crud_intent, regex_extract as cu02_extract
from app.orchestrator.cu03.extractors import regex_extract as cu03_extract, extract_cu03_crud_intent
from app.orchestrator.cu04.extractors import extract_question
from app.services.phishing_analysis import _calculate_score, _PART_STOPWORDS


# ── CU-02 Regresiones ─────────────────────────────────────────────────────────

class TestCU02Regresiones:

    def test_actualizar_solo_no_lanza_excepcion(self):
        # BUG: el patrón r"^\s*(actualizar|...)\s*$" en _UPDATE_TAGS_PATTERNS
        # no tiene grupo "domain". Antes se hacía m.group("domain") → KeyError.
        # Fix: cambiar a m.groupdict().get("domain").
        result = extract_crud_intent("actualizar")
        assert result["intent"] == "update_tags"
        assert result["domain_name"] is None   # no explota, devuelve None

    def test_ver_solo_detecta_lista(self):
        # BUG: el patrón standalone "ver" no estaba en _LIST_PATTERNS.
        # El usuario escribía "ver" y el sistema no lo reconocía como listar.
        result = extract_crud_intent("ver")
        assert result["intent"] == "list"

    def test_status_ingles_invalido(self):
        # BUG: antes el status se guardaba como "active"/"inactive" (inglés).
        # Tras refactor a "activo"/"inactivo", los valores ingleses deben
        # ser rechazados por _validate_domain_name (no aplica directamente,
        # pero verificamos que el extractor mapea correctamente a español).
        result = extract_crud_intent("desactivar prueba.com")
        assert result["new_status"] == "inactivo"   # no "inactive"

    def test_activar_mapea_a_activo(self):
        result = extract_crud_intent("activar prueba.com")
        assert result["new_status"] == "activo"     # no "active"

    def test_cancelar_en_delete_no_rompe(self):
        # BUG: _wants_exit no estaba implementado en _handle_delete.
        # Este test verifica que el extractor al menos no confunde
        # "cancelar" con una intención de borrado.
        result = extract_crud_intent("cancelar")
        assert result["intent"] is None

    def test_tags_maximo_10(self):
        # La especificación se dice máximo 10 tags. El extractor debe truncar.
        mensaje = "acme.io tags: a, b, c, d, e, f, g, h, i, j, k, l"
        result = cu02_extract(mensaje)
        assert len(result.get("tags", [])) <= 10


# ── CU-01 Regresiones ─────────────────────────────────────────────────────────

class TestCU01Regresiones:

    def test_stopwords_excluidas_del_analisis_partes(self):
        # BUG (Fix 5): "login-paypa1.com" → partes ["login", "paypa1"].
        # "login" tenía 93% similitud con "logmein" → falso positivo.
        # Fix: _PART_STOPWORDS excluye "login" del análisis de partes.
        assert "login" in _PART_STOPWORDS
        assert "secure" in _PART_STOPWORDS
        assert "bank" in _PART_STOPWORDS
        assert "verify" in _PART_STOPWORDS

    def test_ip_como_dominio_sube_score(self):
        # Una URL con IP en lugar de nombre de dominio es señal de phishing.
        # El scoring debe detectarlo y añadir puntos.
        score, _, indicators = _calculate_score(
            "192.168.1.1",
            {"creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc)},
            {"providers": {"virustotal": {"malicious": 0, "suspicious": 0}}},
            None,
        )
        assert score >= 10
        assert any("IP" in i or "dirección" in i for i in indicators)

    def test_score_no_supera_100_con_todo_negativo(self):
        # Invariante: el score siempre está entre 0 y 100.
        # Con todos los factores al máximo no debe superarse.
        score, _, _ = _calculate_score(
            "login-paypal-secure.tk",
            {"creation_date": datetime.now(timezone.utc) - timedelta(days=1)},
            {"providers": {"virustotal": {"malicious": 50, "suspicious": 20}}},
            ("paypal.com", 0.99),
        )
        assert 0 <= score <= 100

    def test_vt_cero_no_suma_puntos(self):
        # Si VirusTotal no detecta nada, no debe contribuir al score.
        score_base, _, _ = _calculate_score(
            "google.com",
            {"creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc)},
            {"providers": {"virustotal": {"malicious": 0, "suspicious": 0}}},
            None,
        )
        # El indicador de VT no debe aparecer
        _, _, indicators = _calculate_score(
            "google.com",
            {"creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc)},
            {"providers": {"virustotal": {"malicious": 0, "suspicious": 0}}},
            None,
        )
        assert not any("VirusTotal" in i for i in indicators)


# ── CU-03 Regresiones ─────────────────────────────────────────────────────────

class TestCU03Regresiones:

    def test_nombre_muy_corto_no_se_extrae(self):
        # El nombre de alerta debe tener mínimo 3 caracteres.
        # "ab" solo tiene 2 → no debe extraerse.
        result = cu03_extract("alerta: ab")
        assert "rule_name" not in result

    def test_email_no_se_confunde_con_dominio_scope(self):
        # BUG latente: el email contiene un dominio. Si el extractor
        # no limpia el texto antes de buscar dominios, añade el dominio
        # del email también al scope.
        # Fix: regex_extract hace _EMAIL_RE.sub(" ", text) antes de buscar dominios.
        result = cu03_extract("notifícame en admin@empresa.com para prueba.com")
        domains = result.get("scope", {}).get("domains", [])
        assert "empresa.com" not in domains   # el dominio del email no entra en scope
        assert "prueba.com" in domains

    def test_intent_none_cuando_no_hay_crud(self):
        result = extract_cu03_crud_intent("quiero crear una alerta nueva")
        assert result["intent"] is None


# ── CU-04 Regresiones ─────────────────────────────────────────────────────────

class TestCU04Regresiones:

    def test_consultar_rag_solo_no_es_pregunta(self):
        # El usuario escribe "consultar base de conocimiento" para seleccionar
        # el menú, no para hacer una pregunta. Debe devolver None.
        assert extract_question("consultar base de conocimiento") is None

    def test_numero_4_no_es_pregunta(self):
        assert extract_question("4") is None

    def test_pregunta_real_no_confundida_con_menu(self):
        # Una pregunta que contenga "conocimiento" pero no sea solo la selección
        # de menú debe tratarse como pregunta.
        result = extract_question("¿Qué técnicas de phishing atacan el conocimiento del usuario?")
        assert result is not None
        assert len(result) > 10

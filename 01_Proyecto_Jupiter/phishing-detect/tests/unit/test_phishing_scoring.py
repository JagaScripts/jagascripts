from datetime import datetime, timezone, timedelta
from app.services.phishing_analysis import _calculate_score, parse_input, _extract_brand


class TestExtractBrand:
    def test_dominio_simple(self):
        assert _extract_brand("paypal.com") == "paypal"

    def test_dominio_con_subdominio(self):
        assert _extract_brand("login.paypal.com") == "paypal"

    def test_dominio_gob(self):
        # "agenciatributaria.gob.es" → extrae "agenciatributaria" no "gob"
        assert _extract_brand("agenciatributaria.gob.es") == "agenciatributaria"

    def test_dominio_typosquatting(self):
        assert _extract_brand("paypa1-login.tk") == "paypa1-login"


class TestParseInput:
    def test_url_https(self):
        domain, type_ = parse_input("https://paypal-secure.com/login")
        assert domain == "paypal-secure.com"
        assert type_ == "url"

    def test_dominio_simple(self):
        domain, type_ = parse_input("paypal-secure.com")
        assert domain == "paypal-secure.com"
        assert type_ == "domain"

    def test_email(self):
        domain, type_ = parse_input("usuario@banco.es")
        assert domain == "banco.es"
        assert type_ == "email"

    def test_url_con_path(self):
        domain, type_ = parse_input("http://evil.tk/phishing/login.html")
        assert domain == "evil.tk"
        assert type_ == "url"


class TestCalculateScore:
    def _rep(self, malicious=0, suspicious=0):
        return {"providers": {"virustotal": {"malicious": malicious, "suspicious": suspicious}}}

    def _whois(self, days_ago: int):
        return {"creation_date": datetime.now(timezone.utc) - timedelta(days=days_ago)}

    def test_dominio_limpio_score_bajo(self):
        score, level, _ = _calculate_score(
            "google.com",
            self._whois(3000),
            self._rep(0, 0),
            None,
        )
        assert score < 31
        assert level == "bajo"

    def test_vt_malicioso_sube_score(self):
        score_limpio, _, _ = _calculate_score("evil.com", self._whois(3000), self._rep(0, 0), None)
        score_malo, _, _ = _calculate_score("evil.com", self._whois(3000), self._rep(10, 5), None)
        assert score_malo > score_limpio

    def test_dominio_muy_nuevo_sube_score(self):
        score_nuevo, _, indicators = _calculate_score(
            "nuevositio.xyz",
            self._whois(2),
            self._rep(0, 0),
            None,
        )
        assert score_nuevo >= 25
        assert any("días" in i for i in indicators)

    def test_tld_sospechoso(self):
        score, _, indicators = _calculate_score(
            "sitio.tk",
            self._whois(3000),
            self._rep(0, 0),
            None,
        )
        assert any(".tk" in i for i in indicators)

    def test_typosquatting_sube_score(self):
        score_sin, _, _ = _calculate_score("paypal.com", self._whois(3000), self._rep(0, 0), None)
        score_con, _, _ = _calculate_score(
            "paypa1.com",
            self._whois(3000),
            self._rep(0, 0),
            ("paypal.com", 0.92),
        )
        assert score_con > score_sin

    def test_score_maximo_100(self):
        score, _, _ = _calculate_score(
            "login-paypal-secure.tk",
            self._whois(1),
            self._rep(30, 10),
            ("paypal.com", 0.95),
        )
        assert score <= 100

    def test_niveles_de_riesgo(self):
        # Score bajo
        _, level, _ = _calculate_score("google.com", self._whois(3000), self._rep(0, 0), None)
        assert level == "bajo"

        # Score crítico (VT alto + nuevo + typosquatting)
        _, level, _ = _calculate_score(
            "paypa1.tk",
            self._whois(1),
            self._rep(20, 5),
            ("paypal.com", 0.95),
        )
        assert level in ("alto", "critico")

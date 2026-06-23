import pytest
from datetime import datetime, timezone


@pytest.fixture
def whois_domain_nuevo():
    """WHOIS de dominio recién registrado (2 días de antigüedad)."""
    return {
        "creation_date": datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ).__class__(
            datetime.now(timezone.utc).year,
            datetime.now(timezone.utc).month,
            max(1, datetime.now(timezone.utc).day - 2),
            tzinfo=timezone.utc,
        ),
    }


@pytest.fixture
def whois_domain_viejo():
    """WHOIS de dominio con más de 2 años de antigüedad."""
    return {"creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc)}


@pytest.fixture
def reputation_limpia():
    """Reputación sin detecciones en VirusTotal."""
    return {"providers": {"virustotal": {"malicious": 0, "suspicious": 0}}}


@pytest.fixture
def reputation_maliciosa():
    """Reputación con 5 motores marcando como malicioso."""
    return {"providers": {"virustotal": {"malicious": 5, "suspicious": 2}}}

from __future__ import annotations

import requests
from typing import Any
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.core.settings import settings
from .base import ReputationProvider

logger = get_logger("virustotal_client")


class VirusTotalProvider(ReputationProvider):
    """ Proveedor de reputación usando VirusTotal API v3 """

    BASE_URL = "https://www.virustotal.com/api/v3/domains"

    def __init__(self, api_key: str | None = None):
        """
        Inicializa el cliente de VirusTotal

        Args:
            api_key(str | None): API key de VirusTotal. Si es None, usa settings.virustotal_api_key
        """
        self.api_key = api_key or settings.virustotal_api_key
        if not self.api_key:
            logger.warning("VirusTotal API key no configurada")

    @staticmethod
    def malicious_to_score(malicious: int, suspicious: int) -> float:
        """Convierte conteo de detecciones a score de riesgo (0-100).

        Escala directa por umbrales, usada tanto en análisis puntual (CU-01)
        como en reputación de dominio registrado (CU-02).

        Args:
            malicious(int): Número de motores que marcan como malicioso.
            suspicious(int): Número de motores que marcan como sospechoso.

        Returns:
            float: Score de riesgo entre 0 y 100.
        """
        if malicious >= 6:
            return 100.0
        if malicious >= 3:
            return 75.0
        if malicious >= 1:
            return 50.0
        if suspicious >= 3:
            return 37.5
        if suspicious >= 1:
            return 20.0
        return 0.0

    def check_reputation(self, domain_name: str) -> dict[str, Any]:
        """
        Verifica reputación en VirusTotal

        Args:
            domain_name(str): Nombre del dominio

        Returns:
            dict[str, Any]: Datos de reputación
        """
        if not self.api_key:
            return {
                "provider": "virustotal",
                "malicious": None,
                "suspicious": None,
                "risk_score": 0,
                "last_check_at": None,
                "error": "API key no configurada",
            }

        try:
            url = f"{self.BASE_URL}/{domain_name}"
            headers = {"x-apikey": self.api_key}

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            analysis = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})

            malicioso = analysis.get("malicious", 0)
            sospechoso = analysis.get("suspicious", 0)
            risk_score = self.malicious_to_score(malicioso, sospechoso)

            logger.info(
                f"VirusTotal: {domain_name} - malicioso={malicioso}, sospechoso={sospechoso}, score={risk_score}",
                extra={"event": "virustotal_check", "domain": domain_name},
            )

            return {
                "provider": "virustotal",
                "malicious": malicioso,
                "suspicious": sospechoso,
                "risk_score": risk_score,
                "last_check_at": datetime.now(timezone.utc),
                "error": None,
            }

        except requests.exceptions.RequestException as e:
            type_error = ""
            if e.response is not None and e.response.status_code == 401:
                type_error = "Fallo en la API_KEY de VirusTotal"
                logger.error(
                    f"Error APIKEY de VirusTotal: {domain_name}",
                    extra={"event": "virustotal_apikey_error", "domain": domain_name, "error": type_error},
                )
            else:
                type_error = str(e)
                logger.error(
                    f"Error en VirusTotal API: {domain_name}",
                    extra={"event": "virustotal_error", "domain": domain_name, "error": type_error},
                )
            return {
                "provider": "virustotal",
                "malicious": None,
                "suspicious": None,
                "risk_score": 0,
                "last_check_at": None,
                "error": type_error,
            }

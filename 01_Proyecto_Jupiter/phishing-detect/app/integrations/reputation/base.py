from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ReputationProvider(ABC):
    """
    Clase abstracta para proveedores de reputación de dominios.
    Todos los proveedores deben heredar de esta clase.
    """

    @abstractmethod
    def check_reputation(self, domain_name: str) -> dict[str, Any]:
        """
        Verifica la reputación de un dominio

        Args:
            domain_name (str): Nombre del dominio

        Returns:
            dict: Datos de reputación con estructura:
            {
                "proveedor": "nombre_proveedor",
                "malicioso": 0,
                "sospechoso": 1,
                "risk_score": 15,  # 0-100
                "ultima_comprobacion": datetime,
                "error": None  # o mensaje de error
            }
        """
        pass

from __future__ import annotations

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import requests

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger("notifier")


def _send_email(to: str, subject: str, body: str) -> dict[str, Any]:
    """
    Envía un email notificando la alerta

    Args:
        to(str): Dirección de email de destino
        subject(str): Asunto del email
        body(str): Cuerpo del mensaje en texto plano

    Returns:
        dict[str, Any]: Resultado con 'sent' (bool) y 'error' (str | None)
    """
    if not settings.smtp_user or not settings.smtp_password:
        return {"sent": False, "error": "SMTP no configurado (smtp_user/smtp_password vacíos)"}
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from or settings.smtp_user
        msg["To"] = to
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            from_addr = settings.smtp_from or settings.smtp_user
            server.sendmail(from_addr, to, msg.as_string())

        return {"sent": True, "error": None}
    except Exception as e:
        logger.error(
            f"Error enviando email a {to}",
            extra={"event": "notifier_email_error", "to": to, "error": str(e)},
            exc_info=True,
        )
        return {"sent": False, "error": str(e)}


def _send_webhook(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Envía una notificación HTTP POST a un webhook

    Args:
        url(str): URL del webhook destino
        payload(dict[str, Any]): Datos a enviar en el cuerpo JSON

    Returns:
        dict[str, Any]: Resultado con 'sent' (bool) y 'error' (str | None)
    """
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return {"sent": True, "error": None}
    except Exception as e:
        logger.error(
            f"Error enviando webhook a {url}",
            extra={"event": "notifier_webhook_error", "url": url, "error": str(e)},
            exc_info=True,
        )
        return {"sent": False, "error": str(e)}


def send_notification(
    channel: dict[str, Any],
    rule_name: str,
    user_id: str,
    triggered_domains: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Envía una notificación por el canal configurado.

    Args:
        channel(dict[str, Any]): Canal con 'kind' (email/webhook/in_app) y 'to' (destino)
        rule_name(str): Nombre de la regla que disparó la alerta
        user_id(str): Identificador del usuario
        triggered_domains(list[dict[str, Any]]): Dominios que cumplen la condición

    Returns:
        dict[str, Any]: Resultado con 'sent' (bool) y 'error' (str | None)
    """
    kind = channel.get("kind")
    to = channel.get("to", "")

    if kind == "email":
        subject = f"[Phishing Detect] Alerta: {rule_name}"
        lines = [f"La alerta '{rule_name}' se ha disparado para los siguientes dominios:\n"]
        for d in triggered_domains:
            lines.append(f"  • {d['domain_name']}: {json.dumps(d['details'], ensure_ascii=False)}")
        body = "\n".join(lines)
        return _send_email(to, subject, body)

    if kind == "webhook":
        payload = {
            "event": "alert_triggered",
            "rule_name": rule_name,
            "user_id": user_id,
            "domains": triggered_domains,
        }
        return _send_webhook(to, payload)

    if kind == "in_app":
        # in_app: el registro en AlertEvent lo hace el scheduler, aquí solo confirmamos
        return {"sent": True, "error": None}

    return {"sent": False, "error": f"Canal desconocido: {kind}"}

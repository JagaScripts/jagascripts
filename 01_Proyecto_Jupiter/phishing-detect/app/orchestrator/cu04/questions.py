def ask_for_question() -> str:
    """Solicita al usuario que formule su pregunta sobre phishing."""
    return (
        "¿Sobre qué aspecto del phishing quieres consultar la base de conocimiento?\n\n"
        "Puedes preguntarme cosas como:\n"
        "· ¿Qué es el phishing?\n"
        "· ¿Cómo detectar un correo de phishing?\n"
        "· ¿Qué debo hacer si recibo un correo sospechoso?\n\n"
        "_(Escribe **cancelar** para volver al menú)_"
    )

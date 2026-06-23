class Config:
    """
    Centralized configuration values for the landing page.

    Keeping all user-editable content here cleanly separates data from
    presentation (SRP - Single Responsibility Principle).
    """

    # Content Variables
    FULL_NAME = "Jose Antonio González Alcántara"
    JOB_TITLE = "Python Backend & AI Developer, Cloud Computing & DevOps Expert"
    ALIAS_NAME = "JAGA Scripts"
    PHONE_NUMBER = "695375698"
    EMAIL_ADDRESS = "jagascripts@gmail.com"

    # Identifiers & Usernames
    USERNAME = "JagaScripts"
    GITHUB_HANDLE = "@JagaScripts"

    # Link URLs
    GITHUB_URL = "https://github.com/jagaScripts"
    LINKEDIN_URL = "https://www.linkedin.com/in/jagascripts/"
    TWITTER_URL = "https://x.com/JagaScripts"

    # --- About Me Section ---
    BIO_LINES = [
        "Sobre Jose Antonio González Alcántara — @jagaScripts",
        "",
        "[Experiencia] Software Developer con 4 años trabajando",
        "  para clientes de primer nivel: FC Barcelona, La Caixa,",
        "  Abertis, GBfoods, Berge y mas, en sectores como Banca,",
        "  Infraestructuras, Gran Consumo, Logistica y Deporte.",
        "",
        "[Trayectoria]",
        "",
        "  . T-Systems Iberia - Semi-Senior Software Developer",
        "    Sep 2024 - Jun 2025",
        "    Integracion de ServiceNow, Jira y Zendesk con C# y APIs.",
        "    Metodologia Agile Scrum. Stack: .NET, MVC, POO,",
        "    Git, Copilot, ChatGPT, Visual Studio, VS Code.",
        "    Clientes: La Caixa, Abertis, Autopistas, GBfoods,",
        "    Campofrio, M.C. Mutual, Further, FC Barcelona.",
        "",
        "  . T-Systems Iberia - RPA Developer Expert",
        "    Jul 2023 - Ago 2024",
        "    Automatizacion de +250.000 solicitudes manuscritas",
        "    con OCR e IA. Migracion y refactorizacion critica",
        "    de flotas de robots.",
        "    Cliente: Berge (Logistica y Automacion).",
        "",
        "  . T-Systems Iberia - RPA Developer Junior",
        "    Jul 2022 - Jun 2023",
        "    Extraccion automatizada de imagenes desde Power BI",
        "    con scroll dinamico y envio automatico de reportes.",
        "    Eliminacion del 90%% del tiempo manual de envio.",
        "    Cliente: T-Systems (Consultoria IT).",
        "",
        "[Formacion]",
        "",
        "  . Master en Inteligencia Artificial, Cloud Computing",
        "    & DevOps - PontIA.tech (2025 - Actualidad)",
        "    Stack: Python, FastAPI, Docker, Qdrant, AWS, Azure,",
        "    Machine Learning, Deep Learning, LLMs,",
        "    Prompt Engineering, CI/CD, DevOps.",
        "",
        "  . Grado en Ingenieria Informatica - UAB Barcelona",
        "    120 Creditos ECTS superados.",
        "",
        "  . Bootcamp Full Stack con Java y Angular - 300h (2022)",
        "",
        "  . Curso Superior en Java y Android - 450h (2019)",
        "    18 Creditos ETC.",
        "",
        "[Motivacion] Construir soluciones escalables, limpias y",
        "  mantenibles. Aprendizaje continuo y trabajo en equipo.",
    ]

    EDUCATION_ITEMS = [
        {"label": "Master IA, Cloud & DevOps", "sub": "PontIA.tech · 2025-Actualidad"},
        {"label": "Grado Ingenieria Informatica", "sub": "UAB Barcelona · 120 ECTS"},
        {"label": "Bootcamp Full Stack Java+Angular", "sub": "300h · 2022"},
        {"label": "Curso Superior Java y Android", "sub": "450h · 2019"},
    ]

    SKILLS = {
        "Lenguajes de programacion que he aprendido": [
            "Python", "Java", "JavaScript", "TypeScript", "C#",
            "C++", "C", "VB", "PHP", "HTML5", "CSS3",
        ],
        "Frameworks, Librerias y Bases de Datos": [
            "Node.js", "Angular", "Spring", "Bootstrap", ".NET",
            "FastAPI", "Requests", "Maven", "PrimeFaces",
            "MySQL", "MongoDB", "PostgreSQL", "MariaDB", "Qdrant",
        ],
        "Sistemas, Cloud y DevOps": [
            "Windows", "Linux", "AWS", "Azure", "Google Cloud",
            "Docker", "Kubernetes", "CI/CD", "Git", "GitHub", "GitLab",
        ],
        "Herramientas, IDEs e Inteligencia Artificial": [
            "VS Code", "NetBeans", "Visual Studio", "Eclipse",
            "UiPath", "Orchestrator UiPath", "Jira", "SNOW", "Zendesk",
            "Copilot", "ChatGPT", "Cursor", "Gemini", "OCR",
            "APIs IA", "Antigravity", "Deep Learning", "ML", "RAG", "LLMs",
        ],
    }



def export_context_from_config() -> dict:
    """Return a dictionary of public, UPPERCASE attributes from Config.

    Jinja can access dict keys with dot notation, so we keep the
    template API ergonomic as `context.FULL_NAME`, etc.
    """

    context: dict[str, str] = {}
    for attribute_name in dir(Config):
        if attribute_name.isupper() and not attribute_name.startswith("_"):
            context[attribute_name] = getattr(Config, attribute_name)
    return context


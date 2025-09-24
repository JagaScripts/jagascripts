class Config:
    """
    Centralized configuration values for the landing page.

    Keeping all user-editable content here cleanly separates data from
    presentation (SRP - Single Responsibility Principle).
    """

    # Content Variables
    FULL_NAME = "Jose Antonio González Alcántara"
    JOB_TITLE = "Full Stack Developer"
    PHONE_NUMBER = "695375698"
    EMAIL_ADDRESS = "jagascripts@gmail.com"

    # Identifiers & Usernames
    USERNAME = "JagaScripts"
    GITHUB_HANDLE = "@JagaScripts"

    # Link URLs
    GITHUB_URL = "https://github.com/jagaScripts"
    LINKEDIN_URL = "https://www.linkedin.com/in/jagascripts/"
    TWITTER_URL = "https://x.com/JagaScripts"


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


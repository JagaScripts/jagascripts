from flask import Blueprint

main = Blueprint(
    "main",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/main-static",
)

from . import routes  # noqa: E402,F401  # import routes to register view functions


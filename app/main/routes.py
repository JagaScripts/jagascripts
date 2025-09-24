from flask import render_template

from config import export_context_from_config
from . import main


@main.route("/")
def index():
    context = export_context_from_config()
    return render_template("index.html", context=context)


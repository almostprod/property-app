from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="templates", static_folder="assets")

from . import routes  # noqa isort:skip

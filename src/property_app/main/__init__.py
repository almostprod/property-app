from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="templates")

from . import events  # noqa isort:skip
from . import jobs  # noqa isort:skip
from . import routes  # noqa isort:skip

from flask import render_template

from property_app.logging import get_logger
from property_app.main import bp as main


log = get_logger("property_app.main")


@main.route("/")
def index():
    log.info("index route")

    return render_template("index.html")



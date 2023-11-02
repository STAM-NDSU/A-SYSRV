from flask import Blueprint, render_template, current_app

bp = Blueprint("web", __name__)


@bp.route("/", methods=["GET"])
def index():
    current_app.logger.info("hello")
    return render_template("pages/index.html")

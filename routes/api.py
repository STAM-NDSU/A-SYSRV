from flask import Blueprint, jsonify
import logging
from controllers.api_controller import APIController

logger = logging.getLogger(__name__)
bp = Blueprint("api", __name__, url_prefix="/api")
api_controller = APIController()


@bp.route("/upload_fasta", methods=["POST"])
def upload_fasta():
    return api_controller.upload_fasta()

@bp.route("/download_file", methods=["POST"])
def download_file():
    return api_controller.download_file()

@bp.route("/status", methods=["GET"])
def health_check():
    logger.info("Health check ok.")
    return jsonify("Success"), 200

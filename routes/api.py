from flask import Blueprint, stream_with_context, Response
import logging
from controllers.api_controller import APIController
import time

logger = logging.getLogger(__name__)
bp = Blueprint("api", __name__, url_prefix="/api")
api_controller = APIController()


@bp.route("/upload_fasta", methods=["POST"])
def upload_fasta():
    return api_controller.upload_fasta()

@bp.route("/download_file", methods=["POST"])
def download_file():
    return api_controller.download_file()

@bp.route('/status')
def status():
    def generate():
        logger.info("Starting SSE stream")
        try:
            yield "data: Upload started\n\n"
            logger.info("Yielded: Upload started")
            # ... Other steps with logging ...
            yield "data: Predictions are being made...\n\n"
            logger.info("Yielded: Predictions are being made...")
            # ...
        except GeneratorExit:
            logger.info("Stream closed by the client")
        except Exception as e:
            logger.exception("Unhandled exception in SSE stream")
        finally:
            logger.info("Ending SSE stream")

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'  # Disable caching of the response
    return response




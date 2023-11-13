import logging
from services.uniprot_service import UniportService
from flask import request, jsonify, current_app, send_from_directory
import traceback
import os
import json
from utils.utils import *
from ml.model import MLModel
from controllers.base_controller import BaseController


class APIController(BaseController):
    def __init__(self):
        super().__init__()
        self.uniprot_service = UniportService()
        self.ml_model = MLModel()

    def upload_fasta(self):
        try:
            file = request.files["file"]
            if not file:
                return jsonify("File Not Found"), 419

            # get JSON response from UNIPROT
            results = self.uniprot_service.process_fasta(file)

            # # TODO: Implement ML prediction
            # predictions = self.ml_model.get_predictions(result)
            filename = self.uniprot_service.save_model_response(results)

            return jsonify({"results": results, "filename": filename})
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e)
            return jsonify(str(e)), 400

        # Save Model response

    def download_file(self):
        filename = request.form.get('filename')
        try:
            if not filename:
                return jsonify("File Not Found"), 419

            return send_from_directory("storage/artifacts", filename)
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e)
            return jsonify(str(e)), 400

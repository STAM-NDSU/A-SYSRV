import logging
from services.uniprot_service import UniportService
from flask import request, jsonify
import traceback
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
            # predictions = self.ml_model.get_predictions(results)

            return results
        except Exception as e:
            traceback.print_exc()
            self.logger.error(e)
            return jsonify(str(e)), 400

import logging
from ml.iFeature.iFeatureExtraction import generate_iFeature
from flask import current_app, jsonify
import os
from ml.populate import populate_db
from utils.utils import *
from ml.base_ml import BaseML
from ml.predict import predict_with_model


class MLModel(BaseML):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    # TODO: Implement ML predictions
    def get_predictions(self, user_fasta, uniprot_results):

        try:
            #iFeature
            output_directory = current_app.config.get("IFEATURE")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            generate_iFeature(user_fasta, output_directory)
            self.logger.info(f"iFeature generated")

            #DB
            db_dir = current_app.config.get("DB")
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)

            filename = f"{get_current_datetime()}.db"
            full_filepath = f"{db_dir}/{filename}"

            populate_db(user_fasta, uniprot_results, full_filepath, output_directory)
            self.logger.info(f"DB populated")

            #Predict
            model_dir = current_app.config.get("MODEL")
            model_path = f"{model_dir}/RandomForestClassifier.pkl"

            predictions = predict_with_model(full_filepath, model_path)

            return predictions
        except Exception as e:
            self.logger.error(str(e))
            raise e
import requests
from Bio import SeqIO
import json
from utils.utils import *
import logging
import os
from io import StringIO
from flask import current_app
from services.base_service import BaseService
import pandas as pd


class UniportService(BaseService):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    # Fetch results from UNIPROT
    def get_uniprot_results_by_id(self, id):
        base_url = current_app.config.get("UNIPROT_URL")
        params = {"format": "json", "query": f"accession:{id}"}
        self.logger.info(f"Fetching uniprot results for {id}")
        response = requests.get(base_url, params=params)
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            return result
        return None

    # Process a FASTA file
    def process_fasta(self, fasta_file):
        try:
            self.logger.info("START process fasta")
            result = {}
            content = fasta_file.read().decode("utf-8")
            fasta_content = StringIO(content)
            sequences = SeqIO.parse(fasta_content, "fasta")
            for record in sequences:
                accession_id = record.id.split("|")[1]
                res = self.get_uniprot_results_by_id(accession_id)
                if res:
                    result[accession_id] = res
            self.logger.info("END process fasta")
            self.save_uniprot_response(result)
            return result
        except Exception as e:
            self.logger.error(str(e))
            raise e

    # Save UNIPROT response
    def save_uniprot_response(self, res):
        self.logger.info("SAVE UNIPROT response")

        dir = current_app.config.get("UNIPROT_LOGS")
        if not os.path.exists(dir):
            os.makedirs(dir)

        output_file = f"{dir}/{get_current_datetime()}.json"
        with open(output_file, "w") as json_file:
            json.dump(res, json_file, indent=4)
        return output_file

    # Save Model response
    def save_model_response(self, res):
        self.logger.info("SAVE Model response")

        dir = current_app.config.get("ARTIFACTS")
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = f"{get_current_datetime()}.csv"
        full_filepath = f"{dir}/{filename}"
        res.to_csv(full_filepath, index=False)
        return filename

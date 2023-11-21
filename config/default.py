from flask import current_app
import os


def get_absolute_path(path):
    return os.path.join(current_app.root_path, path)


UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_LOGS = get_absolute_path("storage/uniprot")
LOGS = get_absolute_path("storage/logs")
ARTIFACTS = get_absolute_path("storage/artifacts")
FASTAS = get_absolute_path("storage/fastas")
IFEATURE = get_absolute_path("ml/iFeature")
DB = get_absolute_path("ml/data")
MODEL = get_absolute_path("ml/models")

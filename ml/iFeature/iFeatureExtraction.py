import subprocess
import os
import logging
import sys

logger = logging.getLogger(__name__) # TODO: why not workign?

def generate_iFeature(input_file, output_directory, descriptors=None):

    if descriptors is None:
        descriptors = ["DPC", "CTDC", "CTDT", "CTDD", "CTriad", "GAAC"]
        # PAAC, Moran is not working

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    python_executable = sys.executable

    for descriptor in descriptors:
        logger.info(f"Processing descriptor: {descriptor}")
        command = [python_executable, "./ml/iFeature/iFeature.py", "--file", input_file, "--type", descriptor]
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the encoding.tsv file exists
        source_path = "encoding.tsv"
        if os.path.exists(source_path):
            destination_path = os.path.join(output_directory, f"{descriptor}.tsv")
            os.rename(source_path, destination_path)
            
            # Check if the file is empty
            if os.path.getsize(destination_path) == 0:
                logger.warning(f"The file {destination_path} is empty.")
            else:
                logger.info(f"Descriptor {descriptor} processed successfully.")
        else:
            logger.error(f"Failed to process descriptor {descriptor}.")
            logger.error(f"Error Output: {result.stderr}")

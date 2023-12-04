import subprocess
import os
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)  # Add a stream handler to output to console
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def generate_iFeature(input_file, output_directory, descriptors=None):
    logger.info("Starting iFeature generation")

    if descriptors is None:
        descriptors = ["DPC", "CTDC", "CTDT", "CTDD", "CTriad", "GAAC"]
        # PAAC, Moran is not working
    logger.info(f"Using descriptors: {descriptors}")

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    logger.info(f"Output directory '{output_directory}' created or already exists")

    python_executable = sys.executable

    for descriptor in descriptors:
        logger.info(f"Processing descriptor: {descriptor}")

        try:
            command = [python_executable, os.path.join(os.path.dirname(__file__), "iFeature.py"), "--file", input_file, "--type", descriptor]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Error processing descriptor {descriptor}")
                logger.error(f"Standard Output: {result.stdout}")
                logger.error(f"Standard Error: {result.stderr}")
                continue

            source_path = os.path.join(os.path.dirname(__file__), "encoding.tsv") 
            if os.path.exists(source_path):
                destination_path = os.path.join(output_directory, f"{descriptor}.tsv")
                os.rename(source_path, destination_path)
                logger.info(f"File moved to {destination_path}")

                if os.path.getsize(destination_path) == 0:
                    logger.warning(f"The file {destination_path} is empty.")
                else:
                    logger.info(f"Descriptor {descriptor} processed successfully.")
            else:
                logger.error(f"Failed to find the encoding.tsv file for descriptor {descriptor}.")
        except Exception as e:
            logger.exception(f"An exception occurred while processing descriptor {descriptor}: {e}")

    logger.info("iFeature generation completed")
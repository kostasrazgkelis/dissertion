import os
import logging
import sys

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('flask_app')

# Base path where Spark files will be stored
BASE_SPARK_PATH = "/data/spark/"

# Input and output paths for Spark
SPARK_INPUT_PATH = os.path.join(BASE_SPARK_PATH, "input")
SPARK_OUTPUT_PATH = os.path.join(BASE_SPARK_PATH, "output")

UPLOAD_FOLDER = '/static_files/uploaded_files/'

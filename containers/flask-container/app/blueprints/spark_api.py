# app/blueprints/spark_api.py
from flask import Blueprint, jsonify, make_response
from pyspark.sql import functions as F
import os
from config import SPARK_INPUT_PATH, SPARK_OUTPUT_PATH
from connector import create_spark_session

spark_api = Blueprint('spark_api', __name__)

@spark_api.route('/api/v1/spark/wordcount/', methods=['GET'])
def run_spark_job():
    try:
        spark = create_spark_session()

        df = spark.read.text(os.path.join(SPARK_INPUT_PATH, "alice_in_wonderland.txt"))

        word_counts = df.select(F.explode(F.split(df.value, " ")).alias("word")) \
            .groupBy("word") \
            .count()
        
        word_counts.write.mode('overwrite') \
            .csv(os.path.join(SPARK_OUTPUT_PATH, "word_count_output"))
        
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    else:
        return make_response(jsonify({"message": "Spark job completed successfully"}), 200)
    finally:
        # Stop the Spark session
        spark.stop()

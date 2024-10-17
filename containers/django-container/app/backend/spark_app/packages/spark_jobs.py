from pyspark.sql import Row, SparkSession
from backend.settings import SPARK_URL_INPUT, SPARK_URL_OUTPUT
import os
from backend.logger import logger

class SparkJobLocal:
    def __init__(self, app_name, input_data, spark_id):
        self.app_name = app_name
        self.spark_id = spark_id
        self.input_data = os.path.join(SPARK_URL_INPUT, self.spark_id)
        self.output_data = os.path.join(SPARK_URL_OUTPUT, self.spark_id)
        self.spark = None

    def start_spark(self):
        self.spark = SparkSession.builder.master("local[*]").appName(self.app_name).getOrCreate()

    def stop_spark(self):
        if self.spark: self.spark.stop()

    def handle_exception(self, exception):
        logger.error(f"An error occurred: {exception}")
        return exception

    def run(self):
        raise NotImplementedError("Subclasses should implement this method")
    
class WordCountJob(SparkJobLocal):
    def __init__(self):
        super().__init__(app_name="WordCountApp")

    def run(self):
        try:
            self.start_spark()
            text_file = self.spark.read.text(self.input_data)

            word_counts = text_file.rdd.flatMap(lambda line: line.value.split(" ")) \
                                    .map(lambda word: (word, 1)) \
                                    .reduceByKey(lambda a, b: a + b)
            
            word_counts_df = word_counts.map(lambda x: Row(word=x[0], count=x[1])).toDF()

            word_counts_df.write.csv(self.output_data, header=True, mode="overwrite")

        except Exception as e:
            self.handle_exception(e)
        finally:
            self.stop_spark()
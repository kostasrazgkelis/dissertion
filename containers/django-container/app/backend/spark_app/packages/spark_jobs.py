from pyspark.sql import Row, SparkSession, DataFrame
from backend.settings import SPARK_URL
import os
from documents_app.models import Document

class SparkJobLocal:
    def __init__(self, app_name, matching_list: list, user_data: list[dict], spark_id: str):
        self.app_name = app_name
        self.matching_list = matching_list
        self.user_data = user_data
        self.spark_id = spark_id
        self.output_data =  os.path.join(SPARK_URL, spark_id, 'output')
        self.spark = None

    def start_spark(self):
        self.spark = SparkSession.builder.master("local[*]").appName(self.app_name).getOrCreate()

    def stop_spark(self):
        if self.spark: self.spark.stop()

    def handle_exception(self, exception):
        raise Exception(exception)

    def run(self):
        raise NotImplementedError("Subclasses should implement this method")
    
# class WordCountJob(SparkJobLocal):
#     def __init__(self):
#         super().__init__(app_name="WordCountApp")

#     def run(self):
#         try:
#             self.start_spark()
#             text_file = self.spark.read.text(self.input_data)

#             word_counts = text_file.rdd.flatMap(lambda line: line.value.split(" ")) \
#                                     .map(lambda word: (word, 1)) \
#                                     .reduceByKey(lambda a, b: a + b)
            
#             word_counts_df = word_counts.map(lambda x: Row(word=x[0], count=x[1])).toDF()

#             word_counts_df.write.csv(self.output_data, header=True, mode="overwrite") 

#         except Exception as e:
#             self.handle_exception(e)
#         finally:
#             self.stop_spark()

class SparkJobDissertion(SparkJobLocal):
    def __init__(self, app_name, matching_list, user_data, spark_id):
        super().__init__(app_name=app_name, 
                        matching_list=matching_list, 
                        user_data=user_data, 
                        spark_id=spark_id)

    def run(self):
        try:
            self.start_spark()

            df_list = []
            for _, user_file_pair in enumerate(self.user_data):
                file_id = user_file_pair["file_uuid"]
                
                document = Document.objects.get(id=file_id)
                if not document:
                    raise Exception(f"Document with id {file_id} not found.")
                
                df = self.spark.read.csv(str(document.file), header=None) 
                df_list.append(df)

            if not df_list:
                raise Exception("No DataFrames to join.")
                

            for enum, df in enumerate(df_list):
                for col in df.columns:
                    if col in self.matching_list:
                        df_list[enum] = df.withColumnRenamed(col, f"matching_{enum}")


            final_df: DataFrame = df_list[0] 
            join_columns = [col for col in final_df.columns if not col.startswith("matching_")] 

            
            for df in df_list[1:]:
                final_df = final_df.join(df, on=join_columns, how='inner')

            final_df.write.csv(self.output_data, header=True, mode="overwrite")

        except Exception as e:
            self.handle_exception(e)
        finally:
            self.stop_spark()
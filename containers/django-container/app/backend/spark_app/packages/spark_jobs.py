from pyspark.sql import Row, SparkSession, DataFrame
from backend.settings import MEDIA_ROOT, SPARK_URL
import os
from documents_app.models import Document
import socket

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

    def start_spark_cluster(self):
        hostname = socket.gethostname()
        localhost_ip = socket.gethostbyname(hostname)

        self.spark = SparkSession.builder \
            .appName("SparkDynamicAllocationTest") \
            .master("k8s://https://192.168.49.2:8443") \
            .config("spark.submit.deployMode", "client") \
            .config("spark.driver.memory", "2G")  \
            .config("spark.driver.host", localhost_ip) \
            .config("spark.kubernetes.driverEnv.SPARK_MASTER_URL", "spark://spark-cluster-master-svc.spark-cluster.svc.cluster.local:7077") \
            .config("spark.kubernetes.driver.label.sidecar.istio.io/injec", "false") \
            .config("spark.kubernetes.driver.request.cores", "100m") \
            .config("spark.kubernetes.driver.request.memory", "100m") \
            .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", MEDIA_ROOT) \
            .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.options.claimName", "spark-cluster-pvc") \
            .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
            .config("spark.kubernetes.authenticate.executor.serviceAccountName", "spark") \
            .config("spark.kubernetes.namespace", "spark-cluster") \
            .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.5.3-debian-12-r0") \
            .config("spark.kubernetes.container.image.pullPolicy", "IfNotPresent") \
            .config("spark.kubernetes.executor.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", MEDIA_ROOT) \
            .config("spark.kubernetes.executor.volumes.persistentVolumeClaim.spark-cluster-pvc.options.claimName", "spark-cluster-pvc") \
            .config("spark.kubernetes.allocation.batch.size", "5") \
            .config("spark.kubernetes.maxPendingPods", "5") \
            .config("spark.executor.memory", "4G") \
            .config("spark.executor.cores", "2")  \
            .config("spark.executor.maxNumFailures", "2") \
            .config("spark.kubernetes.driver.pod.name", hostname) \
            .config("spark.kubernetes.executor.label.sidecar.istio.io/injec", "false") \
            .config("spark.kubernetes.executor.deleteOnTermination", "true") \
            .config("spark.kubernetes.executor.request.cores", "2") \
            .config("spark.kubernetes.executor.limit.cores", "2") \
            .config("spark.kubernetes.executor.podPendingTimeout", "600s") \
            .config("spark.kubernetes.executor.keepAliveInterval", "600s") \
            .config("spark.kubernetes.executor.reuseAttempts", "15") \
            .config("spark.dynamicAllocation.enabled", "true") \
            .config("spark.dynamicAllocation.initialExecutors", "1") \
            .config("spark.dynamicAllocation.minExecutors", "1") \
            .config("spark.dynamicAllocation.maxExecutors", "3") \
            .config("spark.dynamicAllocation.executorIdleTimeout", "60s") \
            .config("spark.dynamicAllocation.schedulerBacklogTimeout", "50s") \
            .config("spark.dynamicAllocation.sustainedSchedulerBacklogTimeout", "50s") \
            .config("spark.scheduler.maxRegisteredResourcesWaitingTime", "120s") \
            .config("spark.executorEnv.LD_PRELOAD", "/opt/bitnami/common/lib/libnss_wrapper.so") \
            .getOrCreate()
    
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
            self.start_spark_cluster()
            # self.start_spark()

            df_list = []
            for _, user_file_pair in enumerate(self.user_data):
                file_id = user_file_pair["file_uuid"]
                
                document = Document.objects.get(id=file_id)
                if not document:
                    raise Exception(f"Document with id {file_id} not found.")
                
                file_path: str = os.path.join(MEDIA_ROOT, str(document.file))

                df = self.spark.read.csv(file_path, header=None) 
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
            
            final_df.toPandas().to_csv(os.path.join(self.output_data, "results.csv"), index=False)
            # final_df.write.csv(self.output_data, header=True, mode="overwrite")

        except Exception as e:
            self.handle_exception(e)
        finally:
            self.stop_spark()
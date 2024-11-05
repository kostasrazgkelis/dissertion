from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import SparkContext, SparkConf
from pyspark.sql.types import StringType
import socket

hostname = socket.gethostname()
localhost_ip = socket.gethostbyname(hostname)

try:
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("SparkClusterWordCount") \
        .master("spark://spark-cluster-master-svc.spark-cluster.svc.cluster.local:7077") \
        .config("spark.submit.deployMode", "cluster") \
        .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
        .config("spark.kubernetes.namespace", "spark-cluster") \
        .config("spark.kubernetes.executor.request.cores", "1") \
        .config("spark.kubernetes.executor.limit.cores", "2") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "1g") \
        .config("spark.driver.host", localhost_ip) \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("INFO")
    df = spark.read.text("/data/word_counts.txt")
    # Perform word count
    word_counts = df.select(F.explode(F.split(df.value, " ")).alias("word")) \
        .groupBy("word") \
        .count()
    word_counts.show()
except Exception as e:
    print(e)
finally:
    spark.stop()


from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import SparkContext, SparkConf
from pyspark.sql.types import StringType
import socket

hostname = socket.gethostname()
localhost_ip = socket.gethostbyname(hostname)

try:
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("SparkClusterWordCount") \
        .master("k8s://https://192.168.49.2:8443") \
        .config("spark.submit.deployMode", "client") \
        .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
        .config("spark.kubernetes.namespace", "spark-cluster") \
        .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.5.3-debian-12-r0") \
        .config("spark.kubernetes.executor.request.cores", "1") \
        .config("spark.kubernetes.executor.limit.cores", "2") \
        .config("spark.kubernetes.maxPendingPods", "5") \
        .config("spark.kubernetes.executor.podPendingTimeout", "30s") \
        .config("spark.kubernetes.allocation.batch.size", "1") \
        .config("spark.kubernetes.executor.keepAliveInterval", "30s") \
        .config("spark.kubernetes.executor.reuseAttempts", "5") \
        .config("spark.task.maxFailures", "30") \
        .config("spark.executor.memory", "1g") \
        .config("spark.driver.memory", "1g") \
        .config("spark.driver.host", localhost_ip) \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ALL")
    df = spark.read.text("/data/word_counts.txt")
    # Perform word count
    word_counts = df.select(F.explode(F.split(df.value, " ")).alias("word")) \
        .groupBy("word") \
        .count()
    word_counts.show()
except Exception as e:
    print(e)
finally:
    spark.stop()

# ==============================================================================================================


from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField
import socket
import os

# Get hostname and IP address for the driver configuration
hostname = socket.gethostname()
localhost_ip = socket.gethostbyname(hostname)

try:
    # Initialize SparkSession with dynamic allocation configurations
    spark = SparkSession.builder \
        .appName("SparkDynamicAllocationTest") \
        .master("k8s://https://192.168.49.2:8443") \
        .config("spark.submit.deployMode", "client") \
        .config("spark.driver.memory", "2G")  \
        .config("spark.driver.host", localhost_ip) \
        .config("spark.kubernetes.driverEnv.SPARK_MASTER_URL", "spark://spark-cluster-master-svc.spark-cluster.svc.cluster.local:7077") \
        .config("spark.kubernetes.driver.label.sidecar.istio.io/injec", "false") \
        .config("spark.kubernetes.driver.request.cores", "100m") \
        .config("spark.kubernetes.driver.request.memory", "100m") \
        .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/data") \
        .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.options.claimName", "spark-cluster-pvc") \
        .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
        .config("spark.kubernetes.authenticate.executor.serviceAccountName", "spark") \
        .config("spark.kubernetes.namespace", "spark-cluster") \
        .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.5.3-debian-12-r0") \
        .config("spark.kubernetes.container.image.pullPolicy", "IfNotPresent") \
        .config("spark.kubernetes.executor.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/data") \
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
    spark.sparkContext.setLogLevel("INFO")
    df = spark.read.text("/data/alice_in_wonderland.txt")
    # Perform word count
    word_counts = df.select(F.explode(F.split(df.value, " ")).alias("word")) \
        .groupBy("word") \
        .count()
    word_counts.show()
except Exception as e:
    print(e)
finally:
    spark.stop()

schema = StructType([StructField("word", StringType(), True)])
data = [("word1",), ("word2",), ("word3",), ("word1",)]
df = spark.createDataFrame(data, schema=schema)
# Perform a word count in memory
word_counts = df.groupBy("word").count()
word_counts.show()



from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from flask import Flask, jsonify

# from flask_sqlalchemy import SQLAlchemy
import socket
import os
hostname = socket.gethostname()
localhost_ip = socket.gethostbyname(hostname)
try:
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("SparkDynamicAllocationTest") \
        .master("k8s://https://192.168.49.2:8443") \
        .config("spark.submit.deployMode", "client") \
        .config("spark.driver.memory", "2G")  \
        .config("spark.driver.host", localhost_ip) \
        .config("spark.kubernetes.driverEnv.SPARK_MASTER_URL", "spark://spark-cluster-master-svc.spark-cluster.svc.cluster.local:7077") \
        .config("spark.kubernetes.driver.label.sidecar.istio.io/injec", "false") \
        .config("spark.kubernetes.driver.request.cores", "100m") \
        .config("spark.kubernetes.driver.request.memory", "100m") \
        .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/data") \
        .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.options.claimName", "spark-cluster-pvc") \
        .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
        .config("spark.kubernetes.authenticate.executor.serviceAccountName", "spark") \
        .config("spark.kubernetes.namespace", "spark-cluster") \
        .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.5.3-debian-12-r0") \
        .config("spark.kubernetes.container.image.pullPolicy", "IfNotPresent") \
        .config("spark.kubernetes.executor.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/data") \
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
    # Set log level
    spark.sparkContext.setLogLevel("INFO")
    # Read the text file
    df = spark.read.text("/data/alice_in_wonderland.txt")
    # Perform word count
    word_counts = df.select(F.explode(F.split(df.value, " ")).alias("word")) \
        .groupBy("word") \
        .count()
    word_counts.show()
    # Convert to a Pandas DataFrame and return as JSON
    word_counts_pd = word_counts.toPandas()
    word_counts_dict = word_counts_pd.to_dict(orient='records')
    print(word_counts_dict) 
    print("FINISHED")
except Exception as e:
    print({"error": str(e)})
finally:
    # Stop the Spark session
    spark.stop()

# ==============================================================================================================

from pyspark.sql import Row, SparkSession, DataFrame
import os
import socket

hostname = socket.gethostname()
localhost_ip = socket.gethostbyname(hostname)

spark = SparkSession.builder \
    .appName("SparkDynamicAllocationTest") \
    .master("k8s://https://192.168.49.2:8443") \
    .config("spark.submit.deployMode", "client") \
    .config("spark.driver.memory", "2G")  \
    .config("spark.driver.host", localhost_ip) \
    .config("spark.kubernetes.driverEnv.SPARK_MASTER_URL", "spark://spark-cluster-master-svc.spark-cluster.svc.cluster.local:7077") \
    .config("spark.kubernetes.driver.label.sidecar.istio.io/injec", "false") \
    .config("spark.kubernetes.driver.request.cores", "100m") \
    .config("spark.kubernetes.driver.request.memory", "100m") \
    .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/app/app/backend/static/spark") \
    .config("spark.kubernetes.driver.volumes.persistentVolumeClaim.spark-cluster-pvc.options.claimName", "spark-cluster-pvc") \
    .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark") \
    .config("spark.kubernetes.authenticate.executor.serviceAccountName", "spark") \
    .config("spark.kubernetes.namespace", "spark-cluster") \
    .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.5.3-debian-12-r0") \
    .config("spark.kubernetes.container.image.pullPolicy", "IfNotPresent") \
    .config("spark.kubernetes.executor.volumes.persistentVolumeClaim.spark-cluster-pvc.mount.path", "/app/app/backend/static/spark") \
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
    
matching_list = ['_c0']
user_data  = [{"file_uuid": "/app/app/backend/static/users/1febefa9-a785-4203-b4d0-c8e9e52e6f12/documents/A_cleaned_1.csv"}, 
              {"file_uuid": "http://localhost:8000/static/users/eb510bf0-fce2-4884-a2e0-0c3b6d780868/documents/A_cleaned_2.csv"},
              {"file_uuid": "http://localhost:8000/static/users/7d3a3a8f-8895-4a89-b757-e67c7188be88/documents/A_cleaned_3.csv"}]

df_list = []
for _, user_file_pair in enumerate(user_data):
    file_id = user_file_pair["file_uuid"]
    print(file_id)
    df = spark.read.csv(str(file_id), header=None) 
    df_list.append(df)

if not df_list:
    raise Exception("No DataFrames to join.")
    

for enum, df in enumerate(df_list):
    for col in df.columns:
        if col in matching_list:
            df_list[enum] = df.withColumnRenamed(col, f"matching_{enum}")


final_df: DataFrame = df_list[0] 
join_columns = [col for col in final_df.columns if not col.startswith("matching_")] 


for df in df_list[1:]:
    final_df = final_df.join(df, on=join_columns, how='inner')

final_df.show()

final_df.write.csv(output_data, header=True, mode="overwrite")
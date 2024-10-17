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
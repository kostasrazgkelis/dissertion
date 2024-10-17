import os
import socket
from pyspark.sql import SparkSession

def create_spark_session():
    """
    This function creates and configures a SparkSession for use with Kubernetes or local testing.
    """
    # Get the hostname and IP of the current machine (used in cluster mode)
    hostname = socket.gethostname()
    localhost_ip = socket.gethostbyname(hostname)

    # Determine if we are running locally or in Kubernetes
    if os.getenv("SPARK_HOST") == "k8s":
        # Kubernetes environment configuration
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
    else:
        # Local environment configuration
        spark = SparkSession.builder \
            .appName("LocalSparkApp") \
            .master("local[*]") \
            .config("spark.driver.memory", "2G") \
            .getOrCreate()

    # Set Spark log level
    spark.sparkContext.setLogLevel("INFO")

    return spark

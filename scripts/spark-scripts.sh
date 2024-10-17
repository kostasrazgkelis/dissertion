#!/bin/bash

./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --conf spark.kubernetes.container.image=bitnami/spark:3 \
  --master k8s://192.168.49.2:8443 \
  --conf spark.kubernetes.driverEnv.SPARK_MASTER_URL=spark://spark-master:7077 \
  --conf spark.kubernetes.file.upload.path=/mnt/spark \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=default \
  --conf spark.executor.memory=512m \
  --conf spark.executor.cores=2 \
  --conf spark.kubernetes.executor.request.cores=2 \
  --conf spark.kubernetes.executor.limit.cores=2 \
  --conf spark.kubernetes.executor.request.memory=512m  \
  --conf spark.kubernetes.executor.limit.memory=512m  \
  --deploy-mode cluster \
  ./examples/jars/spark-examples_2.12-3.5.3.jar 1000



./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://localhost:7077 \
  --conf spark.driver.host=localhost \
  --conf spark.default.parallelism=2 \
  --conf spark.executor.cores=1 \
  --conf spark.executor.memory=2G \
  --deploy-mode client \
  ./examples/jars/spark-examples_2.12-3.5.3.jar 100


./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://localhost:7077 \
  --conf spark.driver.host=localhost \
  --conf spark.driver.memory=500M \
  --conf spark.executor.memory=500M \
  --conf spark.executor.cores=1 \
  --deploy-mode client \
  ./examples/jars/spark-examples_2.12-3.5.3.jar 100


./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://spark-master:7077 \
  --conf spark.executor.memory=2G \
  --deploy-mode client \
  ./examples/jars/spark-examples_2.12-3.5.3.jar 100



./bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master local[*] \
  --deploy-mode client \
  --conf spark.driver.memory=2G \
  --conf spark.executor.memory=2G \
  ./examples/jars/spark-examples_2.12-3.5.3.jar 100


  kubectl exec --namespace default spark-cluster-master-0 \
  - spark-submit \
  --master spark://spark-cluster-master-svc:7077  \
  --deploy-mode cluster \
  --conf spark.standalone.submit.waitAppCompletion=true \
  --class org.apache.spark.examples.SparkPi \
  $EXAMPLE_JAR 100
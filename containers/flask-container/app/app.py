from flask import Flask, jsonify
from flask_cors import CORS
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
# from flask_sqlalchemy import SQLAlchemy
import socket
import os

app = Flask(__name__, static_folder='static')
app.config.from_object(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)


# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50), nullable=False)
#     last_name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     age = db.Column(db.Integer, nullable=False)
#     status = db.Column(db.String(20), nullable=False)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "first_name": self.first_name,
#             "last_name": self.last_name,
#             "email": self.email,
#             "age": self.age,
#             "status": self.status
#         }

@app.route('/api/v1/wordcount/', methods=['GET'])
def run_spark_job():

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

        # Convert to a Pandas DataFrame and return as JSON
        word_counts_pd = word_counts.toPandas()
        word_counts_dict = word_counts_pd.to_dict(orient='records')

        return jsonify(word_counts_dict)

    except Exception as e:
        return jsonify({"error": str(e)})
    
    finally:
        # Stop the Spark session
        spark.stop()

@app.route('/api/', methods=['GET'])
def home():
    user_info = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "age": 30,
        "status": "success"
    }
    return jsonify(user_info)

# @app.route('/api/users', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     return jsonify([user.to_dict() for user in users])


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()  # Create database tables for all models
    app.run(host='0.0.0.0', port=8080, debug=os.environ.get('FLASK_DEBUG', False))
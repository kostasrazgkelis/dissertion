from rest_framework import serializers
from .models import User
from spark_app.serializers import  SparkJobListSerializer

class UserSerializer(serializers.ModelSerializer):
    spark_jobs = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'documents', 'spark_jobs']

    def get_spark_jobs(self, obj):
        spark_jobs = obj.get_accessible_spark_jobs()
        return SparkJobListSerializer(spark_jobs, many=True).data
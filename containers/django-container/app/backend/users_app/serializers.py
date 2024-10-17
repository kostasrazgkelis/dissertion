from rest_framework import serializers
from .models import User
from spark_app.serializers import SparkJobListSerializer
from documents_app.serializers import DocumentListSerializer
from documents_app.models import Document
from backend.logger import logger

class UserSerializer(serializers.ModelSerializer):
    spark_jobs = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'documents', 'spark_jobs']

    def get_spark_jobs(self, obj):
        spark_jobs = obj.get_accessible_spark_jobs()
        return SparkJobListSerializer(spark_jobs, many=True).data
    
    def get_documents(self, obj):
        documents = obj.get_documents()
        return DocumentListSerializer(documents, many=True, required=False).data
    
    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        user = User.objects.create(**validated_data)
        for document_data in documents_data:
            Document.objects.create(user=user, **document_data)

        return user
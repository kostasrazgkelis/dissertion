import uuid
from django.db import models
import os
from django.core.validators import FileExtensionValidator
from backend.settings import DOCUMENT_URL

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def get_document_upload_path(instance, filename):
        return os.path.join(DOCUMENT_URL, str(instance.id), 'documents', filename)
    
    documents = models.FileField(upload_to=get_document_upload_path, 
                                 blank=True, 
                                 null=True,
                                 validators=[FileExtensionValidator(allowed_extensions=['csv'])])

    def __str__(self):
        return str(self.id)

    def get_accessible_spark_jobs(self):
        return self.spark_jobs.all()
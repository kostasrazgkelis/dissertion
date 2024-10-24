import uuid
from django.db import models
import os
import shutil
from backend.settings import DOCUMENT_URL

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.id)

    def get_accessible_spark_jobs(self):
        return self.spark_jobs.all()
    
    def get_documents(self):
        return self.documents.all()
    
    def delete(self, *args, **kwargs):
    
        user_folder_path = os.path.join(DOCUMENT_URL, str(self.id))

        if os.path.exists(user_folder_path):
            shutil.rmtree(user_folder_path)

        super().delete(*args, **kwargs)
    
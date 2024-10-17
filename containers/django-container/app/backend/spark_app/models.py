import uuid
from django.db import models
from users_app.models import User
import os
from backend.settings import SPARK_URL_OUTPUT, SPARK_URL_INPUT
from backend.logger import logger

class SparkJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="Spark Job", blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    output_folder = models.CharField(max_length=255, blank=True, null=True)
    input_data_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accessible_users = models.ManyToManyField(User, related_name='spark_jobs', blank=False)

    def __str__(self):
        return str(self.id)


    def save(self, *args, **kwargs):

        if not self.output_folder:
            self.output_folder = os.path.join(SPARK_URL_OUTPUT, str(self.id))
            os.makedirs(self.output_folder, exist_ok=True) 

        if not self.input_data_path:
            self.input_data_path = os.path.join(SPARK_URL_INPUT, str(self.id))
            os.makedirs(self.input_data_path, exist_ok=True) 
        
        super(SparkJob, self).save(using="default", *args, **kwargs)
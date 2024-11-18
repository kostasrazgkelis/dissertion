import uuid
from django.db import models
from users_app.models import User
from documents_app.models import Document
import os
import shutil
from backend.settings import SPARK_URL
from backend.logger import logger

class SparkJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]

    JOBS_CHOICES = [
        ("MULTIPARTY-RL", "Multiparty-Record Linkage")
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="Spark Job", blank=False, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    jobs = models.CharField(max_length=20, choices=JOBS_CHOICES, default='MULTIPARTY-RL')
    output_folder = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    matching_list = models.JSONField(blank=False, null=False, default=list)
    user_data = models.JSONField(blank=False, null=False, default=list)
    accessible_users = models.ManyToManyField(User, related_name='spark_jobs', blank=False)


    def delete(self, *args, **kwargs):
        
        if self.output_folder:
            
            parent_folder = os.path.dirname(self.output_folder)
            if os.path.exists(parent_folder):
                shutil.rmtree(parent_folder)
        
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        if self.matching_list is None:
            self.matching_list = []
        elif not isinstance(self.matching_list, list):
            self.matching_list = list(self.matching_list)
        
        if not isinstance(self.user_data, list):
            raise ValueError("user_data must be a list of dictionaries containing 'user_uuid' and 'file_uuid'.")


        _validated_user_data = []
        _accessible_users = []

        try:

            for entry in self.user_data:
                user_uuid = entry.get('user_uuid')
                file_uuid = entry.get('file_uuid')

                if not user_uuid or not file_uuid:
                    raise ValueError("Each entry in user_data must contain both 'user_uuid' and 'file_uuid'.")

                user = User.objects.get(id=user_uuid)
                document = Document.objects.get(id=file_uuid)

                _validated_user_data.append({"user_uuid": str(user.id), "file_uuid": str(document.id)})
                _accessible_users.append(str(user.id))

            self.user_data = _validated_user_data
            self.accessible_users.set(_accessible_users)  

        except Document.DoesNotExist:
            raise ValueError(f"Document with UUID {file_uuid} does not exist.")
        except User.DoesNotExist:
            raise ValueError(f"User with UUID {user_uuid} does not exist.")
        except Exception as e:
            raise ValueError("Failed to validate user_data or aceessible_users" + str(e))


        if not self.output_folder:
            self.output_folder = os.path.join(SPARK_URL, str(self.id), 'output')
            os.makedirs(self.output_folder, exist_ok=True) 
        
        super(SparkJob, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
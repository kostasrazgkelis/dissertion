import uuid
from django.db import models
import os
from django.core.validators import FileExtensionValidator
from backend.settings import DOCUMENT_URL  # Adjust path based on your project structure

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users_app.User', related_name='documents', on_delete=models.CASCADE)  # Link to the User model
    file_name = models.CharField(max_length=255, blank=True)

    def get_document_upload_path(instance, filename):
        return os.path.join("users", str(instance.user.id), 'documents', filename)

    file = models.FileField(upload_to=get_document_upload_path, 
                            validators=[FileExtensionValidator(allowed_extensions=['csv'])])

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
                     
    def __str__(self):
        return str(self.id)

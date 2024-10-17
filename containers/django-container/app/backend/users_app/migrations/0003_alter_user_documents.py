# Generated by Django 3.2.25 on 2024-10-10 14:42

from django.db import migrations, models
import users_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0002_user_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='documents',
            field=models.FileField(blank=True, null=True, upload_to=users_app.models.User.get_document_upload_path),
        ),
    ]
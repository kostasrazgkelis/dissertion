# Generated by Django 3.2.25 on 2024-10-15 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0004_alter_user_documents'),
        ('spark_app', '0002_auto_20241015_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkjob',
            name='accessible_users',
            field=models.ManyToManyField(related_name='spark_users', to='users_app.User'),
        ),
    ]
# Generated by Django 3.2.25 on 2024-10-15 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0004_alter_user_documents'),
        ('spark_app', '0004_alter_sparkjob_accessible_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkjob',
            name='accessible_users',
            field=models.ManyToManyField(related_name='spark_jobs', to='users_app.User'),
        ),
    ]
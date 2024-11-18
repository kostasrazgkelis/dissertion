from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from users_app.models import User
from documents_app.models import Document
from spark_app.models import SparkJob
import os
from backend.logger import logger

TEST_DOCUMENT_PATH = os.path.join("users_app", "data")

class UserUploadFolderTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(first_name="Alice", last_name="Doe")
        self.user2 = User.objects.create(first_name="Bob", last_name="Doe")
        self.path1 = os.path.join(TEST_DOCUMENT_PATH, "A_cleaned_1.csv")
        self.path2 = os.path.join(TEST_DOCUMENT_PATH, "A_cleaned_2.csv")
        with open(self.path1, 'rb') as file1, open(self.path2, 'rb') as file2:
            self.document_stream_1 = SimpleUploadedFile('A_cleaned_1.csv', file1.read(), content_type="text/csv")
            self.document_stream_2 = SimpleUploadedFile('A_cleaned_2.csv', file2.read(), content_type="text/csv")

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.assertEqual(User.objects.all().count(), 0)


    def test_upload_folder(self):

        url = reverse('user-upload-folder', kwargs={'pk': self.user1.id})  
        response = self.client.post(url, {'documents': [self.document_stream_1]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.filter(user=self.user1).count(), 1)
        documents = Document.objects.filter(user=self.user1)
        self.assertEqual(documents[0].file_name, "A_cleaned_1.csv")
        self.document1 = documents[0]

        url = reverse('user-upload-folder', kwargs={'pk': self.user2.id})  
        response = self.client.post(url, {'documents': [self.document_stream_2]}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.filter(user=self.user2).count(), 1)
        documents = Document.objects.filter(user=self.user2)
        self.assertEqual(documents[0].file_name, "A_cleaned_2.csv")
        self.document2 = documents[0]


    def test_start_spark_job_with_documents(self):
        self.test_upload_folder()

        spark_job_data = {
            'title': "Multiparty-Record-Linkage",
            'matching_list': ["_c0"],
            'user_data': [
                {
                    'user_uuid': self.user1.id,
                    'file_uuid': self.document1.id,
                },
                {
                    'user_uuid': self.user2.id,
                    'file_uuid': self.document2.id,
                }
            ],
        }
        
        
        url = reverse('sparkjob-list') 
        response = self.client.post(url, spark_job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

        spark_job = SparkJob.objects.get(id=response.data['job_id'])

        self.assertEqual(spark_job.status, 'COMPLETED')
        self.assertEqual(os.path.exists(os.path.join(spark_job.output_folder, "_SUCCESS")), True)

        output_folder_path = str(spark_job.output_folder)
        spark_job.delete()

        self.assertEqual(os.path.exists(output_folder_path), False)
        self.assertEqual(SparkJob.objects.all().count(), 0)

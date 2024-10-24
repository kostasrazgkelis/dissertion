import os
import shutil
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import FileResponse
from .packages.spark_jobs import SparkJobDissertion
from .models import SparkJob
from .serializers import SparkJobSerializer
from backend.logger import logger



class SubmitSparkJobViewSet(viewsets.ModelViewSet):
    queryset = SparkJob.objects.all()
    serializer_class = SparkJobSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            spark_job = SparkJob(
                title=serializer.validated_data['title'],
                matching_list=serializer.validated_data['matching_list'],
                status='PENDING'
            )
            spark_job.save()   

            spark_job.user_data = serializer.validated_data['user_data']
            spark_job.status = 'RUNNING'
            spark_job.save()

            # spark = WordCountJob(input_data=serializer.validated_data['input_data_path'],
            #                      spark_id=str(spark_job.id))

            spark = SparkJobDissertion( app_name=spark_job.title,
                                        user_data=spark_job.user_data,
                                        matching_list=spark_job.matching_list,
                                        spark_id=str(spark_job.id)
                                       )
            spark.run()

        except Exception as e:
            spark_job.status = 'FAILED'
            spark_job.save()
            return Response({"error": str(e), 
                             "job_id": str(spark_job.id)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            spark_job.status = 'COMPLETED'
            spark_job.save()

            return Response({"message": "Job completed successfully.", 
                             "job_id": str(spark_job.id)}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            spark_job = self.get_object() 
            serializer = self.get_serializer(spark_job) 
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SparkJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        spark_jobs = self.get_queryset()
        serializer = self.get_serializer(spark_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, pk=None):
        try:

            spark_job = self.get_object()

            if spark_job.status == 'RUNNING':
                return Response({"error": "Cannot delete a running job."}, status=status)
            
            if spark_job.output_folder and os.path.exists(spark_job.output_folder) and os.path.isdir(spark_job.output_folder):
                shutil.rmtree(spark_job.output_folder)

            spark_job.delete()

            return Response({"message": "Spark job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except SparkJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='download-folder')
    def download_folder(self, request, pk=None):
        """Download the output folder of the Spark job as a zip file."""
        try:
            spark_job = self.get_object()

            output_folder = spark_job.output_folder
            if not output_folder or not os.path.exists(output_folder):
                return Response({"error": "Output folder does not exist."}, status=status.HTTP_404_NOT_FOUND)

            zip_file_path = f'/spark/spark-jobs/{spark_job.id}.zip'
            shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', output_folder)

            return FileResponse(open(zip_file_path, 'rb'), as_attachment=True, filename=f'{spark_job.id}.zip')

        except SparkJob.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error while downloading folder: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
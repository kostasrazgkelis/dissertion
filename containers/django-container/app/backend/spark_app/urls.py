from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubmitSparkJobViewSet

router = DefaultRouter()
router.register(r'spark-jobs', SubmitSparkJobViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
]
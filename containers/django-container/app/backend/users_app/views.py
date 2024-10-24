from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer
from documents_app.models import Document

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser)
        
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        return Response(UserSerializer(user).data)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.delete()
        return Response(data={"message": "The user has been deleted"},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_folder(self, request, pk=None):
        user = self.get_object()
        documents_data = request.FILES.getlist('documents')

        if not documents_data:
            return Response({'error': 'No documents provided'}, status=status.HTTP_400_BAD_REQUEST)

        for document in documents_data:
            Document.objects.create(user=user, file=document)

        return Response({'message': 'Documents uploaded successfully'}, status=status.HTTP_201_CREATED)
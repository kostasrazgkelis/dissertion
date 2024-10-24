from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        document = self.get_object()
        return Response(DocumentSerializer(document).data)

    def update(self, request, pk=None):
        document = self.get_object()
        serializer = self.get_serializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            document = serializer.save()
            return Response(DocumentSerializer(document).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        document = self.get_object()
        document.delete()
        return Response(message="The document has been deleted.",
                        status=status.HTTP_204_NO_CONTENT)

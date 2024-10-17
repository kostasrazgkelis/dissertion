from rest_framework import serializers
from .models import SparkJob
from users_app.models import User

class SparkJobSerializer(serializers.ModelSerializer):
    accessible_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        allow_empty=False
    )

    class Meta:
        model = SparkJob
        fields = ['id', 'title', 'status', 'input_data_path', 'output_folder', 'created_at', 'updated_at', 'accessible_users']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Convert the accessible_users queryset to a list of UUIDs for serialization."""
        representation = super().to_representation(instance)
        representation['accessible_users'] = list(instance.accessible_users.values_list('id', flat=True))
        return representation

    def validate_input_data_path(self, value):
        if not value:
            raise serializers.ValidationError("Input data path cannot be empty.")
        return value

    def validate_accessible_users(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least two user UUIDs are required.")
        return value

class SparkJobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparkJob
        fields = ['id'] 

    def to_representation(self, instance):
        return {'id': str(instance.id)}
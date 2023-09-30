from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import TranslationPack


class TranslationPackSerializer(ModelSerializer):
    format_version = serializers.SerializerMethodField()

    class Meta:
        model = TranslationPack
        fields = ['id', 'version', 'format_version', 'name', 'user',
                  'translation_file', 'created_at']

    def get_format_version(self, tr):
        return tr.version / 10

from collections import defaultdict
from django.core.files import File
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import TranslationPackSerializer
from .models import TranslationPack

import json
import os
# Create your views here.


class CreateTranslationPackApiView(generics.CreateAPIView):
    serializer_class = TranslationPackSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        latest = TranslationPack.objects.first()
        data['version'] = latest.version + 1 if latest else 1

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        translation_pack = serializer.save()

        return Response(TranslationPackSerializer(translation_pack).data, status=status.HTTP_201_CREATED)


class UpdateTranslationPackApiView(generics.UpdateAPIView):
    serializer_class = TranslationPackSerializer
    queryset = TranslationPack.objects.all()


class ListAllTranslationPacks(generics.ListAPIView):
    serializer_class = TranslationPackSerializer
    queryset = TranslationPack.objects.all()


class GetLatestTranslationPacks(generics.ListAPIView):
    serializer_class = TranslationPackSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, *args, **kwargs):
        # get the latest translation of each pack
        languages = TranslationPack.objects.values('name').distinct('name')
        packs = TranslationPack.objects.none()
        for language in languages:
            packs = packs | TranslationPack.objects.filter(name=language['name']).order_by('-version')[:1]
        
        return packs


class UploadTranslationCSVApiView(generics.GenericAPIView):
    serializer_class = TranslationPackSerializer
    queryset = TranslationPack.objects.all()

    def post(self, request, *args, **kwargs):
        csv = self.request.FILES.get('translation_file')
        converted_json = self.convert_csv_to_json(csv)

        latest = TranslationPack.objects.order_by('-version').first()
        version = latest.version + 1 if latest else 1

        for key in converted_json:
            with open(f'{key}.json', 'w') as f:
                json.dump(converted_json[key], f)

            with open(f'{key}.json', 'rb') as f:
                serializer = TranslationPackSerializer(
                    data={'name': key,
                          'version': version,
                          'user': request.user.pk,
                          'translation_file': File(f)})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # f.flush()

            f.close()
            os.remove(f'{key}.json')
        return Response({'success': True}, status=status.HTTP_200_OK)

    def convert_csv_to_json(self, csv):
        columns = csv.readline().strip()
        columns = columns.decode('utf-8')
        columns = columns.split(',')
        translation = defaultdict(lambda: defaultdict(dict))
        for line in csv.readlines():
            line = line.strip()
            line = line.decode('utf-8')
            line = line.split(',')
            for i in range(1, len(columns)):
                if line[i] == '':
                    line[i] = line[0]
                translation[columns[i]][line[0]] = line[i]
        return translation

class DeleteTranslationPackApiView(generics.GenericAPIView):
    serializer_class = TranslationPackSerializer
    queryset = TranslationPack.objects.all()
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        translation_pack = self.get_object()
        translation_pack.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)
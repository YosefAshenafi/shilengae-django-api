from django.urls import include, path, re_path
from rest_framework import routers
from .views import CreateTranslationPackApiView, ListAllTranslationPacks, UpdateTranslationPackApiView,\
                    UploadTranslationCSVApiView, GetLatestTranslationPacks, DeleteTranslationPackApiView

urlpatterns = [
    re_path(r'^translation_pack/create/$',
            CreateTranslationPackApiView().as_view(), name='create_translation_pack'),
    re_path(r'^translation_pack/all/$',
            ListAllTranslationPacks().as_view(), name='list_translation_pack'),
    re_path(r'^translation_pack/update/(?P<pk>\d+)/$',
            UpdateTranslationPackApiView().as_view(), name='update_translation_pack'),
    re_path(r'^translation_pack/latest/$',
            GetLatestTranslationPacks().as_view(), name='latest_translation_pack'),
    re_path(r'^translation_pack/upload-csv/$',
            UploadTranslationCSVApiView().as_view(), name='upload_translation_pack'),
    re_path(r'^translation_pack/delete/(?P<pk>\d+)/$',
            DeleteTranslationPackApiView.as_view(), name='delete_translation_pack'),
]

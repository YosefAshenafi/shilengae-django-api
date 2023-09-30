from typing import List
from django.urls import re_path

from .views import CreateAdApiView, DeleteAdApiView, FavoriteAdApiView, FilterAdsByFieldApiView, ListAllAdsApiView, \
    UpdateAdApiView, DetailAdApiView, ListMyAdsApiView, FavoriteAdApiView, \
    ListFavoritedAdsApiView, ReportAdApiView, BrowseAdsApiView, SearchAdsApiView, \
    UploadAdImageApiView, TrendingAdsApiView, UploadMultipleAdImageApiView, UpdateAdPreferenceApiView, \
    GetAdPreferenceApiView, SimilarAdsApiView, FilterAdsByCategoryApiView, \
    BatchDeleteAdsApiView, AdsByUserApiView, ListAllReportedAdsApiView

urlpatterns = [
    re_path(r'^create/$', CreateAdApiView.as_view(), name="create_ad"),
    re_path(r'^image/upload/$', UploadAdImageApiView.as_view(),
            name="upload_ad_image"),
    re_path(r'^image/multiple-upload/$', UploadMultipleAdImageApiView.as_view(),
            name="upload_multiple_ad_image"),
    re_path(r'^update/(?P<pk>\d+)/$',
            UpdateAdApiView.as_view(), name="update_ad"),
    re_path(r'^detail/(?P<pk>\d+)/$',
            DetailAdApiView.as_view(), name="update_ad"),
    # delete ads
    re_path(r'^delete/(?P<pk>\d+)/$',
            DeleteAdApiView.as_view(), name="delete_ad"),
    re_path(r'^delete-batch/$',
            BatchDeleteAdsApiView.as_view(), name="delete_ad_batch"),
    re_path(r'^all/$', ListAllAdsApiView.as_view(), name="list_ads"),
    re_path(r'^list/my-ads/$', ListMyAdsApiView.as_view(), name="list_ads"),
    re_path(r'^list/favorited-ads/$',
            ListFavoritedAdsApiView.as_view(), name="list_favorited_ads"),
    re_path(r'^list/reported-ads/$',
            ListAllReportedAdsApiView.as_view(), name="list_reported_ads"),
    re_path(r'^by-user/(?P<pk>\d+)/$', AdsByUserApiView.as_view(), name="get_ads_by_user"),
    re_path(r'^similar/(?P<pk>\d+)/$',
            SimilarAdsApiView.as_view(), name="similar_ads"),
    re_path(r'^favorite/(?P<pk>\d+)/$',
            FavoriteAdApiView.as_view(), name="favorite_ad"),
    re_path(r'^report/$', ReportAdApiView.as_view(), name="report_ad"),
    re_path(r'^browse/$', BrowseAdsApiView.as_view(), name="browse_ads"),
    re_path(r'^search/$', SearchAdsApiView.as_view(), name="search_ads"),
    re_path(r'^filter/$', FilterAdsByFieldApiView.as_view(), name="filter_ads"),
    re_path(r'^filter-by-category/(?P<pk>\d+)/$',
            FilterAdsByCategoryApiView.as_view(), name="filter_ads_by_category"),
    re_path(r'^trending/$', TrendingAdsApiView.as_view(), name="trending_ads"),
    re_path(r'^update-settings/$', UpdateAdPreferenceApiView.as_view(),
            name="update_settings_ads"),
    re_path(r'^get-settings/$', GetAdPreferenceApiView.as_view(),
            name="get_settings_ads"),

]

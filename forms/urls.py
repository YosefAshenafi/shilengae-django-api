from django.urls import include, path, re_path
from .views import CreateCategoryIconApiView, CreateFormApiView, DeleteCategoryApiView, DeleteFormFieldApiView, GetCategoryFilterStats, ListCategoryIconPackApiView, \
    UpdateCategoryApiView, SearchCategoryApiView, CreateFormApiView, UpdateCategoryIconPackApiView, \
    UpdateFormApiView, CreateFormFieldApiView, UpdateFormFieldApiView,\
    SearchFormApiView, ListFormApiView, ListCategoriesApiView, \
    ListFieldsByFormApiView, CategoryDetailApiView, ListFormFieldByCategoryApiView, \
    DeleteFormApiView, FormDetailApiView, ListSubCategoriesApiView, \
    ListCategoriesByLevelApiView, ListSelectableCategoriesApiView, ListCategoriesByLevelWithSubCategoriesApiView, \
    ListLatestCategoryIconPackApiView, TestView, CreateCategoryApiView, \
    DeleteFormFieldApiView, ListCategoriesWithSubCategoriesApiView, \
    DeleteBatchFormsApiView, ListCategroiesByLevelWithSubCategoriesV2ApiView

urlpatterns = [
    re_path(r'^create/$', CreateFormApiView.as_view(),
            name='form_create'),
    re_path(r'^update/(?P<pk>\d+)/$',
            UpdateFormApiView.as_view(), name='form_update'),
    re_path(r'^detail/(?P<pk>\d+)/$',
            FormDetailApiView.as_view(), name='form_detail'),
    re_path(r'^search/$', SearchFormApiView().as_view(),
            name='form_search'),
    re_path(r'^all/$', ListFormApiView().as_view(),
            name='form_list'),
    re_path(r'^delete/(?P<pk>\d+)/$', DeleteFormApiView().as_view(),
            name='form_delete'),
    re_path(r'^delete-batch/$', DeleteBatchFormsApiView().as_view(),
            name='form_batch_delete'),
    re_path(r'^test/$', TestView.as_view(), name='test'),

    re_path(r'^category/create/$', CreateCategoryApiView.as_view(),
            name='category_create'),
    re_path(r'^category/all/$', ListCategoriesApiView.as_view(),
            name='category_list'),
    re_path(r'^category/level/(?P<level>\d+)/$', ListCategoriesByLevelApiView.as_view(),
            name='category_list_level'),
    re_path(r'^category/level-with-subcategories/(?P<level>\d+)/$', ListCategoriesByLevelWithSubCategoriesApiView.as_view(),
            name='category_list_level_with_subcategories'),
    re_path(r'^category/level-with-subcategories-v2/$', ListCategroiesByLevelWithSubCategoriesV2ApiView.as_view(),
            name='category_list_level_with_subcategories_v2'),
    re_path(r'^category/update/(?P<pk>\d+)/$',
            UpdateCategoryApiView.as_view(), name='category_update'),
    re_path(r'^category/search/$', SearchCategoryApiView().as_view(),
            name='category_search'),
    re_path(r'^category/detail/(?P<pk>\d+)/$', CategoryDetailApiView.as_view(),
            name='category_detail'),
    re_path(r'^category/selectable/$', ListSelectableCategoriesApiView.as_view(),
            name='category_selectable'),
    re_path(r'^category/fields/(?P<pk>\d+)/$', ListFormFieldByCategoryApiView.as_view(),
            name='category_fields'),
    re_path(r'^category/delete/(?P<pk>\d+)/$', DeleteCategoryApiView.as_view(),
            name='category_delete'),
    re_path(r'^category/subcategories/(?P<pk>\d+)/$', ListSubCategoriesApiView.as_view(),
            name='category_subcategories'),
    re_path(r'^category/with-subcategories/$', ListCategoriesWithSubCategoriesApiView.as_view(),
            name='category_with_subcategories'),
    re_path(r'^category/filter-stats/$', GetCategoryFilterStats.as_view(),
            name='category_filter_stats'),


    re_path(r'^category-icon-pack/create/$',
            CreateCategoryIconApiView.as_view(), name='create_category_icon'),
    re_path(r'^category-icon-pack/update/(?P<pk>\d+)/$',
            UpdateCategoryIconPackApiView.as_view(), name='update_category_icon'),
    re_path(r'^category-icon-pack/list/$',
            ListCategoryIconPackApiView.as_view(), name='list_category_icons'),
    re_path(r'^category-icon-pack/latest/$',
            ListLatestCategoryIconPackApiView.as_view(), name='latest_category_icons'),


    re_path(r'^fields/create/$', CreateFormFieldApiView.as_view(),
            name='form_field_create'),
    re_path(r'^fields/(?P<pk>\d+)/$', ListFieldsByFormApiView.as_view(),
            name='form_field_create'),
    re_path(r'^fields/update/(?P<pk>\d+)/$',
            UpdateFormFieldApiView.as_view(), name='form_field_update'),
    re_path(r'^fields/delete/(?P<pk>\d+)/$',
            DeleteFormFieldApiView.as_view(), name='form_field_delete'),
]

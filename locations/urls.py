from ast import Del
from django.urls import include, path, re_path
from rest_framework import routers
from .views import CreateCountryApiView, CreateRegionApiView, CreateCityApiView, DeleteCountryApiView, \
                    EditCountryApiView, EditRegionApiView, EditCityApiView, \
                    ListCountryApiView, ListRegionApiView, ListCityApiView, RegionDetailApiView, \
                    SearchCountryApiView, SearchRegionApiView, SearchCityApiView, \
                    RegionDetailApiView, CityDetailApiView, CountryDetailApiView, \
                    ListCitiesByRegionApiView, ListOperableCountriesApiView, \
                    AddOperableCountryBulkToAdminApiView, AddOperableCountryToAdminApiView, \
                    ChooseOperatingCountryApiView, GetChosenOperatingCountryApiView, \
                    DeleteCityApiView

urlpatterns = [
    re_path(r'^country/create/$', CreateCountryApiView().as_view(), name='create_country'),
    re_path(r'^country/edit/$', EditCountryApiView().as_view(), name='edit_country'),
    re_path(r'^country/delete/(?P<pk>\d+)$', DeleteCountryApiView().as_view(), name='edit_country'),
    re_path(r'^country/all/$', ListCountryApiView().as_view(), name='list_country'),
    re_path(r'^country/operable/$', ListOperableCountriesApiView().as_view(), name='list_operable_countries'),
    re_path(r'^country/search/$', SearchCountryApiView().as_view(), name='search_country'),
    re_path(r'^country/detail/(?P<pk>\d+)$', CountryDetailApiView().as_view(), name='detail_country'),
    re_path(r'^country/operable/add/$', AddOperableCountryToAdminApiView().as_view(), name='add_operable_country'),
    re_path(r'^country/operable/bulk-add/$', AddOperableCountryBulkToAdminApiView().as_view(), name='add_operable_countries'),
    re_path(r'^country/operating/choose/$', ChooseOperatingCountryApiView().as_view(), name='choose_operating_countries'),
    re_path(r'^country/operating/chosen/$', GetChosenOperatingCountryApiView().as_view(), name='choosen_operating_country'),

    re_path(r'^region/create/$', CreateRegionApiView().as_view(), name='create_region'),
    re_path(r'^region/edit/$', EditRegionApiView().as_view(), name='edit_region'),
    re_path(r'^region/all/$', ListRegionApiView().as_view(), name='list_region'),
    re_path(r'^region/search/$', SearchRegionApiView().as_view(), name='search_region'),
    re_path(r'^region/detail/(?P<pk>\d+)$', RegionDetailApiView().as_view(), name='detail_region'),
    
    re_path(r'^city/create/$', CreateCityApiView().as_view(), name='create_city'),
    re_path(r'^city/edit/$', EditCityApiView().as_view(), name='edit_city'),
    re_path(r'^city/all/$', ListCityApiView().as_view(), name='list_city'),
    re_path(r'^city/search/$', SearchCityApiView().as_view(), name='search_city'),
    re_path(r'^city/detail/(?P<pk>\d+)$', CityDetailApiView().as_view(), name='detail_city'),
    re_path(r'^city/delete/(?P<pk>\d+)$', DeleteCityApiView().as_view(), name='delete_city'),
    # get cities by regionId
    re_path(r'^city/by_region/(?P<regionId>\d+)$', ListCitiesByRegionApiView().as_view(), name='detail_city_by_region'),
]
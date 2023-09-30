from django.urls import re_path, include
from .views import LoggedInUserApiView, UpdateUserApiView, SearchUserApiView, \
                    ListUsersApiView, GetUserProfileApiView, UpdateUserProfileApiView, \
                    DeleteUserApiView, DeleteUserByIdApiView, UpdateUserPreferenceApiView, \
                    ListRegularUsersApiView, IsUserRegisteredApiView, UploadUserProfileImageApiView, \
                    UpdateUserPasswordApiView
                    

urlpatterns = [
    re_path(r'^update/(?P<pk>\d+)/$', UpdateUserApiView().as_view(), name='update_user'),
    re_path(r'^update-password/$', UpdateUserPasswordApiView().as_view(), name='update_user_password'),
    re_path(r'^search/$', SearchUserApiView().as_view(), name='search_user'),
    re_path(r'^all/$', ListUsersApiView().as_view(), name='list_user'),
    re_path(r'^list/regular/$', ListRegularUsersApiView().as_view(), name='list_user'),

    re_path(r'^profile/$', LoggedInUserApiView().as_view(), name='logged_in_user_profile'),
    re_path(r'^profile/(?P<pk>\d+)/$', GetUserProfileApiView.as_view(), name='user_profile'),
    re_path(r'^delete/$', DeleteUserApiView.as_view(), name='user_delete'),
    re_path(r'^delete/(?P<pk>\d+)/$', DeleteUserByIdApiView.as_view(), name='user_delete_by_id'),
    re_path(r'^profile/update/$', UpdateUserProfileApiView.as_view(), name='update_user_profile'),

    re_path(r'^preferences/update/(?P<pk>\d+)/$', UpdateUserPreferenceApiView.as_view(), name="update_user_preference"),

    re_path(r'^is-registered/$', IsUserRegisteredApiView.as_view(), name='is_registered'),
]
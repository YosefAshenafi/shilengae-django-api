from django.urls import re_path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from django.views.generic import TemplateView

from .views import FacebookLogin, ConnectToFacebook, LoginWithPhoneApiView, \
                    LoginWithPhoneApiView, LogoutApiView, VerifiedOTPApiView, \
                    UpdatePhoneApiView, GetCurrentAppVersionApiView, FacebookRegistrationApiView, \
                    UpdateAppVersionApiView, ResetPasswordByOTPApiView, RegularRegistrationApiView, \
                    ListTermsAndConditionsApiView, CreateTermsAndConditionsApiView, \
                    GetLatestTermsAndConditionsApiView, UpdateTermsAndConditionsApiView, \
                    CreatePrivacyPolicyApiView, ListPrivacyPolicyApiView, UpdatePrivacyPolicyApiView, \
                    GetLatestPrivacyPolicyApiView, GetIssueReportUrlApiView, CreateIssueReportApiView, \
                    GetStatsApiView

urlpatterns = [
    re_path(r'^token-auth/$', obtain_jwt_token),
    re_path(r'^token-refresh/$', refresh_jwt_token),

    re_path(r'^app-version/$', GetCurrentAppVersionApiView.as_view(), name='app_version'),
    re_path(r'^app-version/update/$', UpdateAppVersionApiView.as_view(), name='update_app_version'),

    re_path(r'^rest-auth/', include('rest_auth.urls')),
    re_path(r'^rest-auth/dashboard-login/$', obtain_jwt_token),
    re_path(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^rest-auth/fb-registration/$', FacebookRegistrationApiView.as_view(), name='fb_register'),

    re_path(r'^rest-auth/fb-login/$', FacebookLogin.as_view(), name='facebook_login'),
    re_path(r'^rest-auth/link-to-facebook/$', ConnectToFacebook.as_view(), name='fb_link'),
    re_path(r'^rest-auth/login-with-phone/$', LoginWithPhoneApiView.as_view(), name="signin_with_phone"),
    re_path(r'^logout/$', LogoutApiView.as_view(), name="logout_"),

    re_path(r'^rest-auth/regular-registration/$', RegularRegistrationApiView.as_view(), name="initial_registration"),
    re_path(r'^rest-auth/verified-otp/$', VerifiedOTPApiView.as_view(), name="verified_otp"),

    re_path(r'^rest-auth/update-phone/$', UpdatePhoneApiView.as_view(), name="update_phone_api"),
    re_path(r'^rest-auth/password/reset-by-otp/$', ResetPasswordByOTPApiView.as_view(), name="reset_password_by_otp"),

    re_path(r'^terms-and-conditions/all/', ListTermsAndConditionsApiView.as_view(), name="list_terms_and_conditions"),
    re_path(r'^terms-and-conditions/create/', CreateTermsAndConditionsApiView.as_view(), name="create_terms_and_conditions"),
    re_path(r'^terms-and-conditions/latest/', GetLatestTermsAndConditionsApiView.as_view(), name="latest_terms_and_conditions"),
    re_path(r'^terms-and-conditions/update/(?P<pk>\d+)/', UpdateTermsAndConditionsApiView.as_view(), name="create_terms_and_conditions"),
    
    re_path(r'^privacy-policy/all/', ListPrivacyPolicyApiView.as_view(), name="list_privacy_policy"),
    re_path(r'^privacy-policy/create/', CreatePrivacyPolicyApiView.as_view(), name="create_privacy_policy"),
    re_path(r'^privacy-policy/latest/', GetLatestPrivacyPolicyApiView.as_view(), name="latest_privacy_policy"),
    re_path(r'^privacy-policy/update/(?P<pk>\d+)/', UpdatePrivacyPolicyApiView.as_view(), name="create_privacy_policy"),

    re_path(r'^issue-report/create/', CreateIssueReportApiView.as_view(), name="create_issue_report_url"),
    re_path(r'^issue-report/get-latest/', GetIssueReportUrlApiView.as_view(), name="get_issue_report_url"),

    re_path(r'^stats/', GetStatsApiView.as_view(), name="get_stats"),
]
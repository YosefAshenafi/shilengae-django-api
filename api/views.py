from django.core.exceptions import ValidationError
from django.db.models.aggregates import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework import serializers
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# from rest_auth.registration.views import SocialLoginView
from rest_auth.app_settings import JWTSerializer
from rest_auth.utils import jwt_encode
from rest_framework.authentication import get_authorization_header
from datetime import timedelta

# Firebase Signup
from firebase_admin import App, auth

from api.models import AppVersion, TermsAndConditions, PrivacyPolicy, ShilengaeIssueReport

from .enums import STATUS
from .mixins import GenerateDataPasswordMixin
from .serializers import FirebaseAuthSerializer, AppVersionSerializer, PasswordResetByOTPSerializer, \
    TermsAndConditionsSerializer, PrivacyPolicySerializer, ShilengaeIssueReportSerializer
from users.models import ShilengaeUser, BlacklistedToken
from users.serializers import ShilengaeUserSignupSerializer,\
    ShilengaeRegularUserSignupSerializer, ShilengaeUpdatePhoneSerializer, \
    ShilengaeFacebookRegisterSerializer, ShilengaeRegularRegisterSerializer
from users.enums import REGISTRATION_METHOD
from users.permissions import AdminPermissions, SuperAdminPermissions
from ads.models import Ad

import random
import string


class ConnectToFacebook(generics.GenericAPIView):
    serializer_class = FirebaseAuthSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        validated = auth.verify_id_token(request.data.get('access_token'))

        # check if this facebook id is already linked to an account
        acct_linked = ShilengaeUser.objects.filter(
            firebase_uid=validated.get('uid')).exists()
        if acct_linked:
            raise serializers.ValidationError(
                'This social account is already linked to a shilengae user')

        user = get_object_or_404(ShilengaeUser, pk=request.user.pk)

        user.firebase_uid = validated.get('uid')
        user.save()

        user.profile.verified_facebook = True
        user.profile.save()

        return Response({'success': True})

# used for migrated users when they signup.
# 1. They would signup with facebook
# 2. They get prompted with phone number and OTP
# 3. They send the facebook access token and phone access token for verification


class ConnectToFacebookWithPhone(generics.GenericAPIView):
    serializers = FirebaseAuthSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        fb_validated = auth.verify_id_token(
            request.data.get('facebook_access_token'))
        phone_validated = auth.verify_id_token(
            request.data.get('phone_access_token'))

        user: ShilengaeUser = ShilengaeUser.objects.filter(
            mobile_number=request.data.get('mobile_number'),
            mobile_country_code=request.data.get('mobile_country_code')).first()

        user.firebase_uid = fb_validated.get('uid')
        user.save()


class FirebaseLogin(generics.GenericAPIView):
    serializer_class = FirebaseAuthSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        # use access_token to get the access_token from firebase and create a new user if it doesn't exist
        validated = auth.verify_id_token(request.data.get('access_token'))

        user = ShilengaeUser.objects.filter(
            firebase_uid=validated.get('uid')).first()
        if not user:
            # TODO: Delete this whole block

            if validated.get('firebase').get('sign_in_provider') == 'phone':
                data = self.generate_user_by_phone(validated)
            elif validated.get('firebase').get('sign_in_provider') == 'facebook.com':
                data = self.generate_user_by_email(validated)
            else:
                # data = self.generate_user_by_email(validated)
                raise serializers.ValidationError('Invalid Signin Provider')

            signup_serializer = ShilengaeUserSignupSerializer(data=data)
            signup_serializer.is_valid(raise_exception=True)
            signup_serializer.save(request=request)

            user = ShilengaeUser.objects.filter(
                firebase_uid=validated.get('uid')).first()

            if validated.get('firebase').get('sign_in_provider') == 'phone':
                user.profile.mobile_number = validated.get('phone_number')
                user.profile.registration_method = validated.get(
                    'firebase').get('sign_in_provider')
                user.profile.verified_mobile = True
                user.profile.save()
            elif validated.get('firebase').get('sign_in_provider') == 'facebook.com':
                user.profile.registration_method = validated.get(
                    'firebase').get('sign_in_provider')
                user.profile.verified_facebook = True
                user.profile.save()

        user = ShilengaeUser.objects.filter(
            firebase_uid=validated.get('uid')).first()
        token = jwt_encode(user)

        user_data = {
            'user': user,
            'token': token
        }

        return Response(JWTSerializer(user_data).data,
                        status=status.HTTP_201_CREATED)

    def generate_user_by_phone(self, validated, request):
        password_requirements = string.ascii_uppercase + \
            string.ascii_lowercase + string.digits + '!#$%'
        username_requirements = string.ascii_lowercase + string.digits

        temp_password = random.sample(password_requirements, 10)
        temp_username = random.sample(username_requirements, 15)

        generated_password = "".join(temp_password)
        generated_username = "".join(temp_username)

        data = {
            # TODO: change this country to get fetched either from frontend or from where the request is coming from
            'country': request.data.get('country', None),
            # TODO: try to fetch from these datas from the request
            'email': '',
            'first_name': generated_username,
            'last_name': '',
            'password1': generated_password,
            'password2': generated_password,
            'status': STATUS.ACTIVE,
            'type': ShilengaeUser.ROLE.USER,
            'username': generated_username,
            'firebase_uid': validated.get('uid')
        }

        return data

    def generate_user_by_email(self, validated, request):
        password_requirements = string.ascii_uppercase + \
            string.ascii_lowercase + string.digits + '!#$%'
        username_requirements = string.ascii_lowercase + string.digits

        temp_password = random.sample(password_requirements, 10)
        temp_username = random.sample(username_requirements, 15)

        generated_password = "".join(temp_password)
        generated_username = "".join(temp_username)

        data = {
            # TODO: change this country to get fetched either from frontend or from where the request is coming from
            'country': request.data.get('country', None),
            # TODO: try to fetch from facebook if auth method is facebook
            'email': '',
            'first_name': validated.get('name').split(' ')[0],
            'last_name': validated.get('name').split(' ')[1],
            'password1': generated_password,
            'password2': generated_password,
            'status': STATUS.ACTIVE,
            'type': ShilengaeUser.ROLE.USER,
            'username': generated_username,
            'firebase_uid': validated.get('uid')
        }

        return data


class FacebookRegistrationApiView(generics.GenericAPIView, GenerateDataPasswordMixin):
    serializer_class = ShilengaeFacebookRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        mobile_country_code = request.data.get('mobile_country_code', '')
        mobile_number = request.data.get('mobile_number', '')

        userQuery = ShilengaeUser.objects.filter(
            mobile_country_code=mobile_country_code, mobile_number=mobile_number)
        if userQuery.exists():
            user = userQuery.first()
            user.firebase_uid = request.data.get('firebase_uid')
            user.save()
        else:
            validated = auth.verify_id_token(request.data.get('access_token'))
            if validated.get('firebase').get('sign_in_provider') != 'phone':
                raise serializers.ValidationError(
                    'Must provide a phone number access token retrieved from firebase')

            data = request.data.copy()
            password = self.generate_password()
            data['type'] = 'USER'
            data['status'] = 'ACTIVE'
            data['password1'] = password
            data['password2'] = password
            data['username'] = self.generate_username()

            serializer = ShilengaeRegularUserSignupSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(request=request)

            user = ShilengaeUser.objects.filter(
                username=serializer.data['username']).first()
            user.profile.registration_method = REGISTRATION_METHOD.FACEBOOK
            user.profile.verified_facebook = True
            user.profile.verified_phone = True
            user.profile.save()

        if user:
            token = jwt_encode(user)
            user_data = {
                'user': user,
                'token': token
            }
            return Response(JWTSerializer(user_data).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FacebookLogin(generics.GenericAPIView):
    serializer_class = FirebaseAuthSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        validated = auth.verify_id_token(request.data.get('access_token'))
        if validated.get('firebase').get('sign_in_provider') != "facebook.com":
            raise serializers.ValidationError(
                'Must provide a facebook access token retrieved from firebase')

        user = ShilengaeUser.objects.filter(
            firebase_uid=validated.get('uid')).first()

        if user:
            token = jwt_encode(user)
            user_data = {
                'user': user,
                'token': token
            }
            return Response(JWTSerializer(user_data).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data={"error": "This user has not yet registered!"},
                            status=status.HTTP_400_BAD_REQUEST)


class RegularRegistrationApiView(generics.GenericAPIView, GenerateDataPasswordMixin):
    serializer_class = ShilengaeRegularRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            access_token = request.data.get('access_token')
            validated = auth.verify_id_token(access_token)
            if validated.get('firebase').get('sign_in_provider') != 'phone':
                raise serializers.ValidationError('Invalid Signin Provider')
        except:
            raise serializers.ValidationError('Invalid Access Token')

        registered = ShilengaeUser.objects.filter(
            firebase_uid=validated.get('uid')).exists()
        if registered:
            return Response({"detail": "There is already a user registered with that phone number"})

        data = {**request.data}
        password = self.generate_password()
        data['username'] = self.generate_username()
        data['type'] = 'USER'
        data['status'] = 'ACTIVE'
        data['password1'] = password
        data['password2'] = password
        data['firebase_uid'] = validated.get('uid')
        data['country'] = request.data.get('country', None)

        serializer = ShilengaeUserSignupSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)

        user = ShilengaeUser.objects.filter(username=data['username']).first()

        user.profile.registration_method = REGISTRATION_METHOD.REGULAR
        user.profile.verified_phone = True
        user.profile.save()

        if user:
            token = jwt_encode(user)
            user_data = {
                'user': user,
                'token': token
            }
            return Response(JWTSerializer(user_data).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdatePhoneApiView(generics.GenericAPIView):
    serializer_class = ShilengaeUpdatePhoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        # update phone number on firebase access_token success
        access_token = request.data.get('access_token')
        validated = auth.verify_id_token(access_token)
        if validated.get('firebase').get('sign_in_provider') != 'phone':
            raise serializers.ValidationError('Invalid Signin Provider')

        # get mobile number and country code from firebase
        phone_number = validated.get('phone_number')
        mobile_country_code = request.data.get('mobile_country_code')
        mobile_number = request.data.get('mobile_number')

        if phone_number != mobile_country_code + mobile_number:
            raise serializers.ValidationError(
                'Firebase phone number and phone number don\'t match')

        user = request.user
        user.mobile_country_code = mobile_country_code
        user.mobile_number = mobile_number
        user.save()

        user.profile.verified_phone = True
        user.profile.save()

        return Response({"detial": "Phone number has been updated"}, status=status.HTTP_200_OK)


class VerifiedOTPApiView(generics.GenericAPIView):
    serializer_class = JWTSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        # validate firebase uid
        validated = auth.verify_id_token(request.data.get('access_token'))
        if validated.get('firebase').get('sign_in_provider') != 'phone':
            raise serializers.ValidationError(
                'Invalid Signin Provider for OTP verification')

        # get phone number from request
        mobile_number = request.data.get('mobile_number')
        mobile_country_code = request.data.get('mobile_country_code')

        # to make sure the request being sent by this phone number is the same as the one on the firebase database
        if validated.get('phone_number') != '{}{}'.format(mobile_country_code, mobile_number):
            raise serializers.ValidationError('Invalid Phone Number')

        # get the user by the phone number and mobile code
        user = ShilengaeUser.objects.filter(
            mobile_number=mobile_number,
            mobile_country_code=mobile_country_code).first()

        # send back a jwt user
        if user:
            token = jwt_encode(user)
            user_data = {
                'user': user,
                'token': token
            }
            return Response(self.get_serializer(user_data).data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutApiView(generics.GenericAPIView):
    serializer_class = JWTSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BlacklistedToken.objects.all()

    def post(self, request, *args, **kwargs):
        auth = get_authorization_header(request).split()
        if auth and len(auth) == 2:
            BlacklistedToken.objects.create(token=auth[1])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise serializers.ValidationError('Invalid Token')


class LoginWithPhoneApiView(generics.GenericAPIView):
    serializer_class = JWTSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        user: ShilengaeUser = ShilengaeUser.objects.filter(
            mobile_number=request.data.get('mobile_number'),
            mobile_country_code=request.data.get('mobile_country_code')).first()

        if user and user.check_password(request.data.get('password')):
            user.last_login = timezone.now()
            user.save()

            token = jwt_encode(user)

            user_data = {
                'user': user,
                'token': token
            }

            return Response(JWTSerializer(user_data).data,
                            status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError('Invalid Credentials', code=status.HTTP_401_UNAUTHORIZED)


class GetCurrentAppVersionApiView(generics.GenericAPIView):
    serializer_class = AppVersionSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        version = AppVersion.objects.first()
        serializer = self.get_serializer(version)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UpdateAppVersionApiView(generics.GenericAPIView):
    serializer_class = AppVersionSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        version = AppVersion.objects.first()
        serializer = self.get_serializer(version, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ResetPasswordByOTPApiView(generics.GenericAPIView):
    serializer_class = PasswordResetByOTPSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ShilengaeUser.objects.all()

    def post(self, request, *args, **kwargs):
        validated = auth.verify_id_token(request.data.get('access_token'))
        if validated.get('firebase').get('sign_in_provider') != 'phone':
            return Response({"success": False, "error": "Invalid Signin Provider for OTP verification"},
                            status=status.HTTP_400_BAD_REQUEST)

        mobile_number = request.data.get('mobile_number')
        mobile_country_code = request.data.get('mobile_country_code')

        if validated.get('phone_number') != '{}{}'.format(mobile_country_code, mobile_number):
            return Response({"success": False, "error": "Phone Number Mismatch"},
                            status=status.HTTP_400_BAD_REQUEST)

        user: ShilengaeUser = ShilengaeUser.objects.filter(
            mobile_number=request.data.get('mobile_number'),
            mobile_country_code=request.data.get('mobile_country_code')).first()

        if not user:
            return Response({"success": False, "error": "User not registered"})

        password1: str = request.data.get('new_password1')
        password2 = request.data.get('new_password2')

        if password1 != password2:
            return Response({"success": False, "error": "Passwords don\'t match"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password1, user)
        except ValidationError as error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password1)
        user.save()

        user.last_login = timezone.now()
        user.save()

        token = jwt_encode(user)

        user_data = {
            'user': user,
            'token': token
        }

        return Response(JWTSerializer(user_data).data,
                        status=status.HTTP_200_OK)


class CreateTermsAndConditionsApiView(generics.CreateAPIView):
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListTermsAndConditionsApiView(generics.ListAPIView):
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TermsAndConditions.objects.all()


class GetLatestTermsAndConditionsApiView(generics.GenericAPIView):
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        terms = TermsAndConditions.objects.order_by('-created_at').first()
        serializer = self.get_serializer(terms)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UpdateTermsAndConditionsApiView(generics.UpdateAPIView):
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TermsAndConditions.objects.all()

    def post(self, request, *args, **kwargs):
        terms = self.get_object()
        serializer = self.get_serializer(terms, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CreatePrivacyPolicyApiView(generics.CreateAPIView):
    serializer_class = PrivacyPolicySerializer
    permission_classes = [permissions.IsAuthenticated]


class ListPrivacyPolicyApiView(generics.ListAPIView):
    serializer_class = PrivacyPolicySerializer
    permission_classes = [permissions.AllowAny]
    queryset = PrivacyPolicy.objects.all()


class GetLatestPrivacyPolicyApiView(generics.GenericAPIView):
    serializer_class = PrivacyPolicySerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        terms = PrivacyPolicy.objects.order_by('-created_at').first()
        serializer = self.get_serializer(terms)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UpdatePrivacyPolicyApiView(generics.UpdateAPIView):
    serializer_class = PrivacyPolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PrivacyPolicy.objects.all()

    def post(self, request, *args, **kwargs):
        terms = self.get_object()
        serializer = self.get_serializer(terms, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GetIssueReportUrlApiView(generics.RetrieveAPIView):
    serializer_class = ShilengaeIssueReportSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return ShilengaeIssueReport.objects.order_by('-created_at').first()


class CreateIssueReportApiView(generics.CreateAPIView):
    serializer_class = ShilengaeIssueReportSerializer
    permission_classes = [permissions.AllowAny]

class GetStatsApiView(generics.GenericAPIView):
    permission_classes = [AdminPermissions | SuperAdminPermissions]

    def get(self, request, *args, **kwargs):
        num_of_ads = Ad.objects.filter(status=STATUS.ACTIVE).count()
        num_of_users = ShilengaeUser.objects.count()
        num_of_users_signed_up_last_month = ShilengaeUser.objects.filter(
            created_at__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)).count()
        num_of_active_users = ShilengaeUser.objects.filter(
            last_login__gte=timezone.now().replace(day=5, hour=0, minute=0, second=0, microsecond=0)).count()
        

        return Response(data={
            'num_of_ads': num_of_ads,
            'num_of_users': num_of_users,
            'num_of_users_signed_up_last_month': num_of_users_signed_up_last_month,
            'num_of_active_users': num_of_active_users
        }, status=status.HTTP_200_OK)
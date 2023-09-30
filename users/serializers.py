from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from rest_framework import serializers
from django.conf import settings

from .models import ShilengaeUser, Country, ShilengaeUserProfile, ShilengaeUserPreference
from api.enums import STATUS


class ShilengaeUserSignupSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(
        required=True,  write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=False, write_only=True)
    status = serializers.ChoiceField(
        choices=STATUS, write_only=True, required=False)
    type = serializers.ChoiceField(
        choices=ShilengaeUser.ROLE, read_only=False, required=False)
    is_guest = serializers.BooleanField(required=False, write_only=True)

    mobile_country_code = serializers.CharField(
        required=True, write_only=True)
    mobile_number = serializers.CharField(required=True, write_only=True)

    business_user = serializers.BooleanField(required=False, write_only=True)
    business_name = serializers.CharField(
        required=False, write_only=True, allow_blank=True)
    operable_countries = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Country.objects.all(), required=False, write_only=True)

    # firebase id token field
    firebase_uid = serializers.CharField(
        required=False, allow_blank=True, write_only=True)

    def custom_signup(self, request, user: ShilengaeUser):
        country = request.data.get('country', None)
        if country:
            country = get_object_or_404(Country, pk=country)

        if (self.validated_data.get('type') == ShilengaeUser.ROLE.SUPERADMIN \
            or self.validated_data.get('type') == ShilengaeUser.ROLE.ADMIN):
                if request.user.is_authenticated and \
                   request.user.type != ShilengaeUser.ROLE.SUPERADMIN:
                    user.delete()
                    raise serializers.ValidationError(
                        {'detail': 'You are not allowed to create a admin/superadmin'})
                
        
        if request.user.is_authenticated and \
                (request.user.type == ShilengaeUser.ROLE.SUPERADMIN or \
                request.user.type == ShilengaeUser.ROLE.ADMIN):
            user.country = request.user.profile.operating_country
        else:
            user.country = country

        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        user.email = self.validated_data.get('email')
        user.status = self.validated_data.get('status')
        user.type = self.validated_data.get('type')
        user.firebase_uid = self.validated_data.get('firebase_uid')
        user.is_guest = self.validated_data.get('is_guest', False)
        user.mobile_country_code = self.validated_data.get(
            'mobile_country_code')
        user.mobile_number = self.validated_data.get('mobile_number')
        user.save()

        if self.validated_data.get('business_user', False):
            user.profile.business_user = self.validated_data.get(
                'business_user', False)
            user.profile.company_name = self.validated_data.get(
                'business_name')
            user.profile.save()

        if user.type == ShilengaeUser.ROLE.ADMIN:
            self.add_operable_countries(user)

    def save(self, request):
        return super(ShilengaeUserSignupSerializer, self).save(request)

    def validate_mobile_number(self, value):
        # check if this mobile_number and mobile_country_code exist in the database
        if value and not self.instance:
            if ShilengaeUser.objects.filter(
                    mobile_number=value,
                    mobile_country_code=self.initial_data.get(
                        'mobile_country_code')).exists():
                raise serializers.ValidationError(
                    'This mobile number is already registered.')
        return value

    def add_operable_countries(self, user: ShilengaeUser):
        if self.context.get('request').user.is_authenticated \
                and self.context.get('request').user.type != ShilengaeUser.ROLE.SUPERADMIN:
            return

        countries = self.validated_data.get('operable_countries', [])
        for country in countries:
            user.profile.operable_countries.add(country)


class ShilengaeRegularUserSignupSerializer(ShilengaeUserSignupSerializer):
    access_token = serializers.CharField(required=True, write_only=True)


class ShilengaeRegularRegisterSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=True)
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)
    firebase_uid = serializers.CharField(required=True)
    business_user = serializers.BooleanField(required=False, write_only=True)
    business_name = serializers.CharField(
        required=False, write_only=True, allow_blank=True)
    access_token = serializers.CharField(required=True)


class ShilengaeFacebookRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), required=True)
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)
    firebase_uid = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True)


class ShilengaeUpdatePhoneSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True, write_only=True)
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)


class ShilengaeUserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=ShilengaeUser.objects.all(), required=False, write_only=True)
    operating_country_name = serializers.SerializerMethodField()

    class Meta:
        model = ShilengaeUserProfile
        fields = ['user', 'registration_method', 'company_name', 'facebook_id',
                  'operating_country', 'profile_picture', 'online_status',
                  'business_user', 'verified_email', 'verified_phone',
                  'verified_facebook', 'operating_country', 'operating_country_name',
                  'fcm_token']
        read_only_fields = ('user',)

    def get_operating_country_name(self, obj):
        if obj.operating_country:
            return obj.operating_country.name
        return None

class ShilengaeUserSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all())
    country_name = serializers.SerializerMethodField()
    profile = ShilengaeUserProfileSerializer(read_only=True, required=False)

    class Meta:
        model = ShilengaeUser
        fields = ['id', 'first_name', 'email', 'last_name', 'username',
                  'status', 'type', 'last_login', 'mobile_country_code',
                  'mobile_number', 'country', 'country_name', 'profile',
                  'firebase_uid', 'created_at', 'last_login']

    def get_country_name(self, obj):
        if obj.country:
            return obj.country.name
    


class ShilengaeUserPreferenceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=ShilengaeUser.objects.all(), required=False, write_only=True)

    class Meta:
        model = ShilengaeUserPreference
        fields = ['user', 'app_notification', 'chat_notification']


class ShilengaeUserDeleteSerializer(serializers.Serializer):
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)

class ShilengaeUserUpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'email_template_name': 'api/password_reset.txt',
            'domain_override': settings.DOMAIN_NAME
        }

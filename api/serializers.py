from rest_framework import serializers

from .models import AppVersion, TermsAndConditions, PrivacyPolicy, ShilengaeIssueReport


class FirebaseAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)

    class Meta:
        fields = ['access_token']

class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ['app_version', 'category_version', 'force_update', 
                  'min_android_version', 'max_android_version', 
                  'min_ios_version', 'max_ios_version']

class PasswordResetByOTPSerializer(serializers.Serializer):
    mobile_country_code = serializers.CharField(required=True)
    mobile_number = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True, allow_blank=False)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['id', 'title', 'content']

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'title', 'content']

class ShilengaeIssueReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShilengaeIssueReport
        fields = ['id', 'issue_submission_url']
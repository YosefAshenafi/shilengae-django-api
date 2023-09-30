from django.db.models.query import QuerySet
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from forms.models import Category, FormField, FormFieldResponse, FormFieldImageResponse
from forms.serializers import CategorySerializer, FormFieldSerializer
from users.models import ShilengaeUser
from users.serializers import ShilengaeUserSerializer

from .models import Ad, ReportedAds, FavoritedAds, ShilengaeAdPreferences


class ImageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldImageResponse
        fields = ['id', 'image']


class ResponsesSerializer(serializers.ModelSerializer):
    images = ImageResponseSerializer(many=True, read_only=True)
    form_field = FormFieldSerializer()

    class Meta:
        model = FormFieldResponse
        fields = ('id', 'form_field', 'images', 'data')

class AdDetailSerializer(serializers.ModelSerializer):
    responses = ResponsesSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    user = ShilengaeUserSerializer(read_only=True)
    favorited = serializers.SerializerMethodField()
    lca_category = serializers.PrimaryKeyRelatedField(
        read_only=True)

    class Meta:
        model = Ad
        fields = ['id', 'category', 'user', 'type', 'status', 'favorited',
                  'lca_category', 'adExpiry', 'responses', 'created_at']
    
    def get_favorited(self, obj):
        if not hasattr(obj, 'favorited') and self.context.get('request', None) and self.context.get('request', None).user.is_authenticated:
            return FavoritedAds.objects.filter(ad=obj, user=self.context.get('request').user).exists()
        elif not hasattr(obj, 'favorited'):
            return False
        return obj.favorited

class AdSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(required=True, queryset=Category.objects.all())
    responses = ResponsesSerializer(many=True, required=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        required=False, queryset=ShilengaeUser.objects.all())

    class Meta:
        model = Ad
        fields = ['id', 'category', 'user', 'type', 'status',
                  'adExpiry', 'responses', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        days = ShilengaeAdPreferences.objects.first().adExpiryDays
        validated_data['adExpiry'] = timezone.now() + timezone.timedelta(days=days)
        # create an empty ad only with the category and user
        ad: Ad = super().create(validated_data)

        # create the form responses from the data
        self.create_form_responses(ad, self.context.get(
            'request').data.get('responses', []))

        return ad

    def update(self, instance, validated_data):
        # update the ad
        instance = super().update(instance, validated_data)

        # update the form responses
        self.update_form_responses(instance, self.context.get(
            'request').data.get('responses', []))

        return instance

    def update_form_responses(self, ad, responses):
        # update the form responses
        # FormResponse => {"form_field": 1, "data": {"value": "option-1"}}
        for response in responses:
            if type(response.get('form_field')) == dict:
                form_field: FormField = get_object_or_404(
                    FormField, pk=response.get('form_field').get('id'))
            else:
                form_field = get_object_or_404(
                    FormField, pk=response.get('form_field'))
            form_response = FormFieldResponse.objects.filter(
                ad=ad,
                form_field=form_field).first()
            form_response.data = response.get('data', {})
            form_response.save()

            if form_field.type == FormField.FORM_TYPE.image:
                self.create_images(form_response, response.get('images'), edit=True)

    def create_form_responses(self, ad, responses):
        # attach the form responses to the ad
        # FormResponse => {"form_field": 1, "data": {"value": "option-1"}}
        for response in responses:
            form_field: FormField = get_object_or_404(
                FormField, pk=response.get('form_field'))
            if (not response.get('data') or response.get('data').get('value')) == '' \
                and FormField.FORM_TYPE.image != form_field.type \
                and form_field.is_required:
                raise serializers.ValidationError(f'{form_field.name} field is required')

            data = response.get('data', {})
            if form_field.type == FormField.FORM_TYPE.price:
                data['price_symbol'] = self.context.get('request').user.country.currency
                data['value'] = float(data.get('value', '0'))

            if type(data.get('value', '0')) is str and data.get('value', '0').isnumeric():
                data['value'] = float(data.get('value', '0'))
            
            self.validate_field(form_field, data.get('value', ''))

            form_response = FormFieldResponse.objects.create(
                ad=ad,
                form_field=form_field,
                user=self.context.get('request').user,
                data=data)
            if form_field.type == FormField.FORM_TYPE.image:
                self.create_images(form_response, response.get('images'))
            elif form_field.type == FormField.FORM_TYPE.file:
                pass

    def create_images(self, form_field_response, images, edit=False):
        if not images:
            raise serializers.ValidationError(
                'No images provided for form field response')

        if edit:
            FormFieldImageResponse.objects.filter(form_field_response=form_field_response).update(form_field_response=None)

        for image_id in images:
            image = get_object_or_404(FormFieldImageResponse, pk=image_id)
            image.form_field_response = form_field_response
            image.save()

    def validate_field(self, form_field: FormField, value):
        if form_field.type == FormField.FORM_TYPE.textbox:
            self.validate_title(form_field, value)
        elif form_field.type == FormField.FORM_TYPE.price:
            self.validate_price(form_field, value)


    def validate_title(self, form_field: FormField, value):
        # min_value, max_value = form_field.data.get('min_value'), form_field.data.get('max_value')
        if len(str(value)) > 50 and form_field.name == 'Title':
            # This needs the form_field name to be 'Title'
            raise serializers.ValidationError('Title cannot be more than 50 characters')
    
    def validate_price(self, form_field, value):
        num, decimal = str(value).split('.')
        if len(num) > 18 or len(decimal) > 2:
            raise serializers.ValidationError('Unrealistic or Invalid Price')

class FavoritedAdsSerializer(serializers.ModelSerializer):
    ad = AdDetailSerializer(read_only=True)

    class Meta:
        model = Ad
        fields = ['ad', 'user', 'created_at']

class ReportedAdsSerializer(serializers.ModelSerializer):
    user = ShilengaeUserSerializer(read_only=True)
    class Meta:
        model = ReportedAds
        fields = ['id', 'ad', 'user', 'report_category', 'description']

class AdPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShilengaeAdPreferences
        fields = ['id', 'adExpiryDays', 'adExpiryEnabled']
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers, validators

from .models import Country, Region, City
from users.models import ShilengaeUser

class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'currency', 'name', 'symbol', 'timezone', 'status', 'created_at']

class AddOperableCountrySerializer(Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=ShilengaeUser.objects.all())
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), many=True)

class AddBulkOperableCountrySerializer(Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=ShilengaeUser.objects.all())
    country_ids = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), many=True)

class ChooseOperatingCountrySerializer(Serializer):
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

class RegionSerializer(ModelSerializer):
    country = CountrySerializer
    country_name = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'symbol', 'country', 'status', 'country_name', 'created_at']
        validators = []

    def create(self, validated_data):
        try:
            Region.objects.get(country=validated_data.get('country'), symbol=validated_data.get('symbol'))
        except Region.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError('Unique Together Country and Symbol')

        region = super().create(validated_data)
        region.country = validated_data.get('country')
        region.save()

        return region

    def get_country_name(self, obj):
        return obj.country.name


class CitySerializer(ModelSerializer):
    region = RegionSerializer
    region_name = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'symbol', 'region', 'status', 'region_name', 'created_at']
        validators=[]

    def create(self, validated_data):
        try:
            City.objects.get(region=validated_data.get('region'), symbol=validated_data.get('symbol'))
        except City.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError(f"There is a City with the symbol {validated_data.get('symbol')} associated with this region.")

        city = super().create(validated_data)
        city.region = validated_data.get('region')
        city.save()

        return city

    def get_region_name(self, obj):
        return obj.region.name

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from .models import Region, City, Country
from .serializers import CountrySerializer, RegionSerializer, CitySerializer, \
    AddOperableCountrySerializer, AddBulkOperableCountrySerializer, \
    ChooseOperatingCountrySerializer
from api.enums import STATUS
from users.models import ShilengaeUser

class CreateCountryApiView(generics.CreateAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateRegionApiView(generics.GenericAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        country_id = request.data.get('country_id', None)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(country=request.user.profile.operating_country)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateCityApiView(generics.GenericAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        region_id = request.data.get('region_id')
        region = get_object_or_404(Region, pk=region_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(region=region)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EditCountryApiView(generics.GenericAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        country_id = request.data.get("country_id")
        country = get_object_or_404(Country, pk=country_id)

        serializer = self.get_serializer(
            country, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)

class DeleteCountryApiView(generics.DestroyAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Country.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EditRegionApiView(generics.GenericAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        region_id = request.data.get("region_id")
        region = get_object_or_404(Region, pk=region_id)

        country_id = request.data.get('country_id')

        serializer = self.get_serializer(
            region, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)


class EditCityApiView(generics.GenericAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        city_id = request.data.get("city_id")
        city = get_object_or_404(City, pk=city_id)

        region_id = request.data.get('region_id')

        serializer = self.get_serializer(city, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if region_id:
            region = get_object_or_404(Region, pk=region_id)
            serializer.save(region=region)
        else:
            serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)

class DeleteCityApiView(generics.DestroyAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = City.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class ListCountryApiView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        if status == 'active':
            return Country.objects.filter(status=STATUS.ACTIVE)
        return Country.objects.all()


class ListOperableCountriesApiView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
            return Country.objects.filter(status=STATUS.ACTIVE)
        return self.request.user.profile.operable_countries.all()

class AddOperableCountryToAdminApiView(generics.GenericAPIView):
    serializer_class = AddOperableCountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Country.objects.all()

    def post(self, request, *args, **kwargs):
        country_id = request.data.get("country_id")
        user_id = request.data.get("user_id")

        country: Country = get_object_or_404(Country, pk=country_id)
        user: ShilengaeUser = get_object_or_404(ShilengaeUser, pk=user_id)

        if user.type != ShilengaeUser.ROLE.ADMIN:
            raise serializers.ValidationError('User is not an admin.')

        # TODO: abstract this to permissions class
        if request.user.type != ShilengaeUser.ROLE.SUPERADMIN:
            raise serializers.ValidationError('You don\'t have privileges to make this request')

        user.profile.operable_countries.add(country)

        return Response(data={"success": True}, status=status.HTTP_200_OK)

class AddOperableCountryBulkToAdminApiView(generics.GenericAPIView):
    serializer_class = AddBulkOperableCountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        country_ids = request.data.get("country_ids")
        user_id = request.data.get("user_id")

        user: ShilengaeUser = get_object_or_404(ShilengaeUser, pk=user_id)

        if user.type != ShilengaeUser.ROLE.ADMIN:
            raise serializers.ValidationError('User is not an admin.')

        for country_id in country_ids:
            country: Country = get_object_or_404(Country, pk=country_id)
            user.profile.operable_countries.add(country)

        return Response(data={"success": True}, status=status.HTTP_200_OK)

class ChooseOperatingCountryApiView(generics.GenericAPIView):
    serializer_class = ChooseOperatingCountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        country_id = request.data.get("country_id")

        country: Country = get_object_or_404(Country, pk=country_id)

        if request.user.type != ShilengaeUser.ROLE.ADMIN and request.user.type != ShilengaeUser.ROLE.SUPERADMIN:
            raise serializers.ValidationError('User is not an admin.')

        request.user.profile.operating_country = country
        request.user.profile.save()

        return Response(data={"success": True}, status=status.HTTP_200_OK)

class GetChosenOperatingCountryApiView(generics.GenericAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        country = request.user.profile.operating_country
        serializer = self.get_serializer(country)

        return Response(serializer.data, status.HTTP_200_OK)

class ListRegionApiView(generics.ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        filter = {}

        if status == 'active':
            filter = {'status': STATUS.ACTIVE, 'country__status': STATUS.ACTIVE}
        if self.request.user.is_authenticated and \
            (self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
             self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN):
            filter['country'] = self.request.user.profile.operating_country
        return Region.objects.filter(**filter)


class ListCityApiView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        filter = {}
        if status == 'active':
            filter = {
                'status': STATUS.ACTIVE,
                'region__status': STATUS.ACTIVE,
                'region__country__status': STATUS.ACTIVE
            }
        if self.request.user.is_authenticated and \
            (self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
             self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN):
            filter = {**filter, 'region__country': self.request.user.profile.operating_country}
        return City.objects.filter(**filter)

class ListCitiesByRegionApiView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        region_id = self.kwargs.get('regionId', None)
        region = get_object_or_404(Region, pk=region_id)
        return City.objects.filter(region=region)


class SearchCountryApiView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        return Country.objects.filter(Q(name__icontains=search_term) |
                                      Q(symbol__icontains=search_term))


class SearchRegionApiView(generics.ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        return Region.objects.filter(Q(name__icontains=search_term) |
                                     Q(symbol__icontains=search_term))


class SearchCityApiView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        return City.objects.filter(Q(name__icontains=search_term) |
                                   Q(symbol__icontains=search_term))


class RegionDetailApiView(generics.RetrieveAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Region.objects.all()


class CountryDetailApiView(generics.RetrieveAPIView):
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Country.objects.all()


class CityDetailApiView(generics.RetrieveAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = City.objects.all()

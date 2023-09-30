from collections import OrderedDict
from django.db.models import Q, Value
from django.db.models.fields import IntegerField
from django.db.models.expressions import OuterRef, Exists, Subquery
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from api.enums import STATUS

from .serializers import AdDetailSerializer, AdSerializer, \
    FavoritedAdsSerializer, ReportedAdsSerializer, AdPreferenceSerializer
from .models import Ad, FavoritedAds, ReportedAds, ShilengaeAdPreferences
from .mixins import TrendingMixin
from .pagination import LimitOffsetWithCategoryPagination
from forms.models import Category, FormFieldResponse, FormFieldImageResponse, UserCategoryFilters
from forms.serializers import FormFieldImageResponseSerializer, FormFieldMultipleImageResponseSerializer
from users.models import ShilengaeUser
from users.permissions import AdminPermissions, SuperAdminPermissions


class UploadAdImageApiView(generics.CreateAPIView):
    serializer_class = FormFieldImageResponseSerializer
    permission_classes = [permissions.IsAuthenticated]


class UploadMultipleAdImageApiView(generics.CreateAPIView):
    serializer_class = FormFieldMultipleImageResponseSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form_data = {}
        response = []
        for images in request.FILES.getlist('images'):
            form_data['image'] = images
            serializer = FormFieldImageResponseSerializer(data=form_data)
            if serializer.is_valid():
                serializer.save()
                response.append(serializer.data)
            else:
                raise serializers.ValidationError(
                    {'success': False, 'message': 'There was a problem uploading images'})

        return Response({
            'success': True,
            'data': response,
        }, status=status.HTTP_201_CREATED)


class CreateAdApiView(generics.CreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeleteAdApiView(generics.GenericAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        ad = get_object_or_404(Ad, pk=kwargs.get('pk'))
        # ad.responses.delete()
        if ad.user == request.user or \
                self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
                self.request.user.type == ShilengaeUser.ROLE.SUPER_ADMIN:
            ad.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class BatchDeleteAdsApiView(generics.GenericAPIView):
    serializer_class = AdSerializer
    permission_classes = [AdminPermissions | SuperAdminPermissions]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        ad_ids = request.data
        if ad_ids:
            Ad.objects.filter(id__in=ad_ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class UpdateAdApiView(generics.UpdateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Ad.objects.all()

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DetailAdApiView(generics.RetrieveAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Ad.objects.prefetch_ad_data().with_favorited(self.request.user)


class ListAllAdsApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Ad.objects.all()
    pagination_class = LimitOffsetWithCategoryPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        filter = {}
        if self.request.user.is_authenticated:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
                    self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
                filter['category__country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['category__country'] = self.request.user.country
        
        if self.request.query_params.get('search'):
            filter['responses__data__value__icontains'] = self.request.query_params.get('search')

        queryset = Ad.objects.prefetch_ad_data().filter(**filter)\
            .with_lca_category()\
            .with_favorited(self.request.user)

        return queryset

class ListAllReportedAdsApiView(generics.ListAPIView):
    serializer_class = ReportedAdsSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ReportedAds.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        filter = {}
        if self.request.user.is_authenticated:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
                    self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
                filter['ad__category__country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['ad__category__country'] = self.request.user.country

        queryset = ReportedAds.objects.filter(**filter)

        return queryset


class ListMyAdsApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user).with_favorited(self.request.user)


class ListFavoritedAdsApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.favorited_ads


class FavoriteAdApiView(generics.GenericAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Ad.objects.all()

    def post(self, request, *args, **kwargs):
        ad: Ad = self.get_object()
        response = ""
        if not FavoritedAds.objects.filter(ad=ad, user=request.user).exists():
            FavoritedAds.objects.create(ad=ad, user=request.user)
            response = "Ad has been added to favorites"
        else:
            FavoritedAds.objects.filter(ad=ad, user=request.user).delete()
            response = "Ad has been removed from favorites"
        return Response({"detail": response}, status=status.HTTP_200_OK)


class ReportAdApiView(generics.GenericAPIView):
    serializer_class = ReportedAdsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ad: Ad = get_object_or_404(Ad, pk=request.data.get('ad'))
        if ad.user == request.user:
            raise serializers.ValidationError(
                {'detail': 'You cannot report your own ad'})

        elif request.user.reported_ads.filter(ad=ad).exists():
            raise serializers.ValidationError(
                {'detail': 'You have already reported this ad'})
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(ad=ad, user=request.user)

            report_count = ReportedAds.objects.filter(ad=ad).count()
            if report_count >= 3:
                ad.status = STATUS.INACTIVE
                ad.save()

            return Response(serializer.data, status=status.HTTP_200_OK)


class ListFavoritedAdsApiView(generics.ListAPIView):
    serializer_class = FavoritedAdsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoritedAds.objects.filter(user=self.request.user)


class FilterAdsByCategoryApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        filter = Q(category=category) | Q(category__ancestors=category)
        print("[FilterAdsByCategoryApiView]: In Get queryset")
        self.add_category_to_user_filters(category)
        return Ad.objects.filter(status=STATUS.ACTIVE).prefetch_ad_data().filter(filter).with_favorited(self.request.user).distinct()

    def add_category_to_user_filters(self, category: Category):
        print("[FilterAdsByCategoryApiView]: Adding Category to Filter Stats")
        if self.request.user.is_authenticated and category:
            print("[FilterAdsByCategoryApiView]: User is Authenticated")
            cat1 = UserCategoryFilters.objects.create(category=category, user=self.request.user)
            print("[FilterAdsByCategoryApiView]: Created UserCategoryFilters", category.name)
            for ancestor in category.ancestors.all():
                UserCategoryFilters.objects.create(category=ancestor, user=self.request.user)
                print("[FilterAdsByCategoryApiView]: Created UserCategoryFilters for ancestor", ancestor.name)


class SearchAdsApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetWithCategoryPagination

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term', "")
        responses = FormFieldResponse.objects.filter(
            data__value__icontains=search_term)
        # TODO: change to subquery
        ad_ids = [response.ad.pk if response.ad else None for response in responses]
        return Ad.objects.filter(id__in=ad_ids).with_favorited(self.request.user).with_lca_category()


class ListAdsWithLCACategoryApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]
    # response needs to have a category field


class FilterAdsByFieldApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LimitOffsetWithCategoryPagination

    @method_decorator(cache_page(60*60*2))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @method_decorator(cache_page(60*60*2))
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        filters = self.request.data.get('filters', [])
        sorting = self.request.data.get('sorting', [])
        title_search = self.request.data.get('search_term', None)
        category_search = self.request.data.get('category', None)

        ads = self.filter_by_fields(filters)

        ads = self.search_by_title(ads, title_search)

        ads = self.filter_by_country_for_user(ads, self.request.user)

        ads = self.filter_by_category(ads, category_search)

        ads = self.sort_ads(ads, sorting)

        return ads.prefetch_ad_data().with_lca_category().with_favorited(self.request.user).filter(price__isnull=False).distinct()

    def filter_by_fields(self, filters):
        response = FormFieldResponse.objects.none()
        if not filters:
            response = FormFieldResponse.objects.all()

        for filter in filters:
            query = Q(form_field=filter.get('form_field', None))

            search_term = filter.get('search_term', None)

            gt = filter.get('gt', None)
            lt = filter.get('lt', None)

            if type(search_term) is str:
                query &= Q(data__value__icontains=search_term)
            elif type(search_term) is list:
                query &= Q(data__value__in=search_term)

            if gt:
                query &= Q(data__value__gte=gt if type(
                    gt) is int else int(gt), data__value__isnull=False)

            if lt:
                query &= Q(data__value__lte=lt if type(
                    lt) is int else int(lt), data__value__isnull=False)

            response = response | FormFieldResponse.objects.filter(query)

        return Ad.objects.prefetch_ad_data().annotate(in_filter=Exists(
            response.filter(ad=OuterRef('id')))).filter(in_filter=True)


    def filter_by_country_for_user(self, ads, user):
        if user.is_anonymous: return ads

        if user.type == ShilengaeUser.ROLE.USER:
            ads = ads.filter(category__country=user.country)
        elif user.type == ShilengaeUser.ROLE.ADMIN or user.type == ShilengaeUser.ROLE.SUPERADMIN:
            ads = ads.filter(
                category__country=user.profile.operating_country)
        return ads

    def filter_by_category(self, ads, category):
        if category:
            ads = ads.filter(Q(category__ancestors=category) | Q(category=category))
        return ads

    def search_by_title(self, ads, title_search):
        if not title_search: return ads

        response = FormFieldResponse.objects.filter(
            data__value__icontains=title_search)
        return ads.annotate(in_search=Exists(response.filter(
            ad=OuterRef('id')))).filter(in_search=True)

    def sort_ads(self, ads, sorting):
        prices = FormFieldResponse.objects.filter(ad=OuterRef(
            'id'), form_field__type='price').values('data__value')
        ads = ads.annotate(price=Subquery(prices))

        if not sorting:
            return ads

        for sort in sorting:
            if sort.get('field') == 'created_at':
                if sort.get('direction') == 'asc':
                    ads = ads.order_by('created_at')
                else:
                    ads = ads.order_by('-created_at')
            elif sort.get('field') == 'price':
                if sort.get('direction') == 'asc':
                    ads = ads.order_by('price')
                else:
                    ads = ads.order_by('-price')

        return ads
class BrowseAdsApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60*60*2))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        # if it's promoted check the promoted expiry date
        # if it's not promoted check the ad expiry date
        filter = {'status': STATUS.ACTIVE}
        if self.request.user and not self.request.user.is_anonymous and self.request.user.type == ShilengaeUser.ROLE.USER:
            filter['category__country'] = self.request.user.country

        preference = ShilengaeAdPreferences.objects.first()
        ads = Ad.objects.prefetch_ad_data().filter(**filter)
        if preference and preference.adExpiryEnabled:
            ads = ads.filter(Q(promoted=True) & Q(promotedExpiry__gte=timezone.now()) |
                             Q(adExpiry__gte=timezone.now()))

        if not self.request.user.is_anonymous:
            ads = ads.with_favorited(self.request.user)

        return ads

class AdsByUserApiView(generics.ListAPIView):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Ad.objects.filter(user=pk)

class TrendingAdsApiView(generics.ListAPIView, TrendingMixin):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60*60*2))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        filter = {'status': STATUS.ACTIVE}
        if self.request.user.is_authenticated and self.request.user.type == ShilengaeUser.ROLE.USER:
            filter['category__country'] = self.request.user.country

        trending_ads = self.sort_by_trending(Ad.objects.filter(**filter))
        return trending_ads.prefetch_ad_data().with_favorited(self.request.user)


class SimilarAdsApiView(generics.ListAPIView, TrendingMixin):
    serializer_class = AdDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        ad = get_object_or_404(Ad, pk=self.kwargs.get('pk'))
        return self.similar_ads(ad).with_favorited(self.request.user)


class UpdateAdPreferenceApiView(generics.GenericAPIView):
    serializer_class = AdPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        preference = ShilengaeAdPreferences.objects.first()
        if not preference:
            serializer = self.get_serializer(data=request.data)
        else:
            serializer = self.get_serializer(preference, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GetAdPreferenceApiView(generics.GenericAPIView):
    serializer_class = AdPreferenceSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        preference = ShilengaeAdPreferences.objects.first()
        return Response(data=self.get_serializer(preference).data, status=status.HTTP_200_OK)

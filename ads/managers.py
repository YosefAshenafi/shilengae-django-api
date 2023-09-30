from django.db import models
from django.db.models import Value, IntegerField, Exists, Count
from django.db.models.expressions import OuterRef


class AdManager(models.Manager):
    pass


class AdQuerySet(models.QuerySet):
    def with_lca_category(self):
        from ads.models import Ad
        lca_category = Ad.get_low_common_ancestor_category(self)

        if lca_category:
            return self.annotate(lca_category=Value(lca_category.pk, output_field=IntegerField()))

        return self

    def with_favorited(self, user):
        from ads.models import FavoritedAds
        if user.is_authenticated:
            return self.annotate(favorited=Exists(FavoritedAds.objects.filter(user=user, ad=OuterRef('id'))))
        else:
            return self.annotate(favorited=Value(False, output_field=models.BooleanField()))

    def fetch_ads_by_users_country(self, user):
        pass

    def fetch_ad_with_reports(self, user):
        from ads.models import ReportedAds
        return self.prefetch_ad_data().annotate(
            report_count=Count(ReportedAds.objects.filter(user=user, ad=OuterRef('id')))
        )

    def prefetch_ad_data(self):
        return self\
            .select_related(
                'category',
                'category__form',
                'category__country', 
                'category__parent', 
                'user', 
                'user__country',
                'user__profile',
                'user__profile__operating_country')\
            .prefetch_related(
                'favoriters',
                'category__ancestors',
                'category__descendants',
                'category__children',
                'category__icon',
                'responses',
                'responses__form_field',
                'responses__images'
            )

from django.db import models

from forms.models import Category
from users.models import ShilengaeUser
from api.models import Activatable, Timestampable

from .enums import TYPE, REPORT_CATEGORIES
from .managers import AdQuerySet, AdManager

# Create your models here.


class Ad(Activatable, Timestampable):
    category = models.ForeignKey(
        Category, related_name='ads', on_delete=models.CASCADE)
    user = models.ForeignKey(
        ShilengaeUser, on_delete=models.CASCADE, related_name='ads')

    type = models.CharField(max_length=10, choices=TYPE, default=TYPE.REGULAR)
    adExpiry = models.DateTimeField(null=True, blank=True)

    # promoted ad field
    promoted = models.BooleanField(default=False)
    promotedExpiry = models.DateTimeField(null=True, blank=True)

    objects = AdManager.from_queryset(AdQuerySet)()

    v1_id = models.IntegerField(null=True, blank=True)

    @staticmethod
    def get_low_common_ancestor_category(ads_queryset):
        """
        Get the lowest common ancestor category of a queryset of ads.
        """
        if ads_queryset.count() == 0:
            return None

        cat_queryset = Category.objects.filter(ads__in=ads_queryset)
        lowest_common_ancestor = cat_queryset.first()

        for category in cat_queryset:
            while lowest_common_ancestor.parent and \
                    category.ancestors.filter(id=lowest_common_ancestor.id).count() == 0:
                lowest_common_ancestor = lowest_common_ancestor.parent

        return lowest_common_ancestor

class FavoritedAds(Timestampable):
    ad = models.ForeignKey(Ad, related_name='favoriters', on_delete=models.CASCADE)
    user = models.ForeignKey(ShilengaeUser, related_name='favorited_ads', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('ad', 'user')

class ReportedAds(Timestampable):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE,
                           related_name='reporters')
    # the person who reported the ad
    user = models.ForeignKey(
        ShilengaeUser, on_delete=models.CASCADE, related_name='reported_ads')
    report_category = models.CharField(
        max_length=20, choices=REPORT_CATEGORIES, default=REPORT_CATEGORIES.FRAUD)
    description = models.CharField(max_length=250)

    class Meta:
        unique_together = ('ad', 'user')


class ShilengaeAdPreferences(Timestampable):
    # this is to indicate if ad expiry is enabled in the app
    adExpiryEnabled = models.BooleanField(default=False)
    # this is to indicate the number of days the ad will be active
    adExpiryDays = models.IntegerField(default=0)

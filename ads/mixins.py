from django.db.models import F, Count, Min, Max, Value
from django.db.models.expressions import ExpressionWrapper
from django.db.models.fields import DateTimeField, FloatField, IntegerField
from django.db.models.functions import Cast
from django.db.models.query_utils import Q

from django.utils import timezone
from datetime import timedelta
from django.db.models import Func, IntegerField
from django.db.models.functions import Abs

from .models import Ad

import random


class Epoch(Func):
    template = 'EXTRACT(epoch FROM %(expressions)s)::INTEGER'
    output_field = IntegerField()


class TrendingMixin:
    def sort_by_trending(self, queryset):
        queryset = queryset.annotate(favorite_count=(Count('favoriters')))
        duration = Epoch(F('now') - F('created_at'))

        queryset = queryset.annotate(
            now=Cast(timezone.now(), DateTimeField()),
            duration=duration,
            # duration2=(Min('duration') / F('duration')),
        )
        agg = queryset.aggregate(
            min_duration=Min('duration'),
            max_favorite=Max('favorite_count')
        )
        min_duration = 0 if not agg.get('min_duration') else agg.get('min_duration') 
        max_favorite = 0 if not agg.get('max_favorite') else agg.get('max_favorite')

        queryset = queryset.annotate(
            duration_factor=ExpressionWrapper(
                float(min_duration) / F('duration'),
                output_field=FloatField()
            ),
            fav_factor=ExpressionWrapper(
                F('favorite_count') / max(1, float(max_favorite)),
                output_field=FloatField()
            ),
            # random_factor=ExpressionWrapper(Value(1.0), output_field=FloatField())
            trending_factor=ExpressionWrapper(
                F('duration_factor') * 0.3 + F('fav_factor') * 0.6,
                output_field=FloatField()
            )
        ).order_by('-trending_factor')
        return queryset

    def similar_ads(self, ad: Ad):
        curr = ad.category
        # Exclude requested ad from the list and include other ads from the same category
        result = Ad.objects.filter(~Q(id=ad.id), category=curr)\
                           .annotate(diff=ExpressionWrapper(
                                            Value(0), 
                                            output_field=IntegerField()))
        while curr:
            # on every level go up the tree and add all ads from that level
            queryset = Ad.objects.filter(
                ~Q(id__in=result.values_list('id')) & ~Q(id=ad.id),
                category__ancestors=curr,
            ).annotate(
                diff=Abs(ExpressionWrapper(
                    Value(curr.level) - Value(ad.category.level),
                    output_field=IntegerField()
                ))
            )
            # add the resulting queryset to the total result
            result = result.union(queryset)

            if result.count() >= 5:
                break

            curr = curr.parent

        # sort the result by the diff field which is their distance from ad
        queryset = result.order_by('diff')[:5]
        ads = []

        for ad in queryset:
            ads.append(ad.id)

        queryset = Ad.objects.filter(id__in=ads)
        return queryset

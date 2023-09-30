from django.db import models
# from django.db.models import Value, IntegerField, Exists
# from django.db.models.expressions import OuterRef


class CategoryManager(models.Manager):
    pass

class CategoryQuerySet(models.QuerySet):
    def prefetch_category_data(self):
        return self\
            .select_related(
                'parent',
                'form'
            )\
            .prefetch_related(
                'descendants',
                'children'
            )
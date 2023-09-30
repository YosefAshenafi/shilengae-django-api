from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import NON_FIELD_ERRORS
from model_utils import Choices
# from jsonfield import JSONField

from .managers import CategoryManager, CategoryQuerySet
from api.models import Timestampable, Activatable
from locations.models import Country
from users.models import ShilengaeUser

# Create your models here.


class Form(Timestampable):
    name = models.CharField(max_length=200)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, related_name="forms")

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'country']


class FormField(Timestampable, Activatable):
    FORM_TYPE = Choices('textbox', 'multiline_textbox', 'dropdown', 'radio',
                        'multi-select', 'image', 'file', 'date', 'date-range',
                        'range', 'region', 'city', 'price')
    type = models.CharField(choices=FORM_TYPE, max_length=50)
    description = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    hint = models.CharField(max_length=50, null=True, blank=True)
    label = models.CharField(max_length=50, null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=True)

    form = models.ForeignKey(Form,
                             related_name='form_fields',
                             null=True,
                             on_delete=models.SET_NULL)
    data = JSONField(null=True)

    class Meta:
        unique_together = ('position', 'form')
        ordering = ['position']


class Category(Timestampable, Activatable):
    name = models.CharField(max_length=100)

    parent = models.ForeignKey('self',
                               related_name='children',
                               null=True,
                               on_delete=models.SET_NULL)

    ancestors = models.ManyToManyField('self',
                                       related_name='+',
                                       symmetrical=False)

    descendants = models.ManyToManyField('self',
                                         related_name='+',
                                         symmetrical=False)

    form = models.ForeignKey(Form,
                             related_name='categories',
                             null=True,
                             on_delete=models.SET_NULL)

    level = models.IntegerField(default=1)

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, related_name="categories")
    
    v1_id = models.IntegerField(null=True, blank=True)

    objects = CategoryManager.from_queryset(CategoryQuerySet)()
    class Meta:
        ordering = ['name']

    def add_parent(self, parent):
        self.parent = parent
        self.add_self_to_parent()
        self.save()

    def add_self_to_parent(self):
        if self.parent:
            self.ancestors.set(self.parent.ancestors.all())
            self.ancestors.add(self.parent)

        for ancestor in self.ancestors.all():
            ancestor.descendants.add(self)

        self.save()

    def get_ancestors(self, include_self):
        """
        get ancestors of categories including self
        """
        if include_self:
            return self.ancestors.all() | Category.objects.filter(id=self.id)
        else:
            return self.ancestors.all()

class UserCategoryFilters(Timestampable):
    category = models.ForeignKey(
        Category, related_name='filters', on_delete=models.CASCADE)
    user = models.ForeignKey(ShilengaeUser,
                             related_name='category_filters',
                             null=True,
                             on_delete=models.SET_NULL)


class CategoryIconPack(Timestampable):
    category = models.ForeignKey(
        Category, related_name='icon', on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='category_icon_packs')
    version = models.IntegerField(default=1)


class FormFieldResponse(Timestampable, Activatable):
    form_field = models.ForeignKey(FormField,
                                   # TODO: make this plural form_fields
                                   related_name='form_field',
                                   null=True,
                                   on_delete=models.SET_NULL)

    user = models.ForeignKey(ShilengaeUser,
                             related_name='+',
                             null=True,
                             on_delete=models.SET_NULL)

    from ads.models import Ad
    ad = models.ForeignKey(Ad,
                           related_name='responses',
                           null=True,
                           on_delete=models.SET_NULL)

    data = JSONField()
    # test

    class Meta:
        unique_together = ('form_field', 'user', 'ad')


class FormFieldImageResponse(Timestampable, Activatable):
    form_field_response = models.ForeignKey(FormFieldResponse,
                                            related_name='images',
                                            null=True,
                                            on_delete=models.SET_NULL)

    image = models.ImageField(
        upload_to='form_field_image_responses', null=True, blank=True)

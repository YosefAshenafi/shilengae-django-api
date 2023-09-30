from django.db import models

from api.models import Activatable, Timestampable
from api.enums import STATUS

class Country(Activatable, Timestampable):
    # Symbol of Currency
    currency = models.CharField(max_length=4)

    # Name of the Country (TODO: link to word)
    name = models.CharField(max_length=100, unique=True)

    # Symbol of the country
    symbol = models.CharField(max_length=5, unique=True)

    # The timezone symbol of the country
    timezone = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Region(Activatable, Timestampable):
    # Name of the Region (TODO: link to word)
    name = models.CharField(max_length=100)

    # Symbol of the Region
    symbol = models.CharField(max_length=5)

    # The country this region belongs to
    country = models.ForeignKey(Country,
                                related_name='regions',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)

    v1_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        unique_together = ('country', 'symbol')


class City(Activatable, Timestampable):
    # Name of the City (TODO: link to word)
    name = models.CharField(max_length=100)

    # Symbol of the Region
    symbol = models.CharField(max_length=5)

    # The region this city belongs to
    region = models.ForeignKey(Region,
                                related_name='cities',
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True)

    v1_id = models.IntegerField(blank=True, null=True)

    longitude = models.DecimalField(max_digits=12, decimal_places=12, blank=True, null=True)

    latitude = models.DecimalField(max_digits=12, decimal_places=12, blank=True, null=True)

    class Meta:
        ordering = ['name']
        unique_together = ('region', 'symbol')

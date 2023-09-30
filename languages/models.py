from django.db import models

# Create your models here.
from django.db import models
from api.models import Timestampable

from users.models import ShilengaeUser


class Word(Timestampable):
    # The definition that this word belongs to
    definition = models.CharField(max_length=500)

    # The default value if the word is not to be found in the language pack
    default = models.CharField(max_length=200)


class TranslationPack(Timestampable):
    version = models.IntegerField()

    name = models.CharField(max_length=50)

    # json files that are translation packs
    translation_file = models.FileField(upload_to='translation_packs')

    # The user that uploaded the translation pack
    user = models.ForeignKey(ShilengaeUser, null=True,
                             on_delete=models.CASCADE)

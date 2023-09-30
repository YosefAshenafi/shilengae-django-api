from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from annoying.fields import AutoOneToOneField
from model_utils import Choices
from django.utils.translation import gettext_lazy as _

from locations.models import Country
from api.models import Timestampable, Activatable
from .enums import REGISTRATION_METHOD

# Create your models here.
class ShilengaeUser(AbstractUser, Timestampable, Activatable):
    username_validator = UnicodeUsernameValidator()

    # This is mainly just used for authenticating the admin user on the dashboard
    username = models.CharField(
        max_length=15,
        unique=True,
        help_text='Required. 15 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    # The first name of the user
    first_name = models.CharField(max_length=50, blank=True)

    # The last name of the user
    last_name = models.CharField(max_length=50, blank=True, null=True)

    # The email of the user
    email = models.EmailField(_('email address'), blank=True, null=True)

    # The country of the user
    country = models.ForeignKey(Country, 
                                related_name='+',
                                null=True,
                                on_delete=models.SET_NULL)

    ROLE = Choices('SUPERADMIN', 'ADMIN', 'MODERATOR', 'GUEST', 'USER')

    # The role of the user
    type = models.CharField(choices=ROLE, max_length=50, default=ROLE.GUEST)

    # The firebase id that is used to authenticate the user
    firebase_uid = models.CharField(max_length=100, blank=True, null=True, default=None, unique=True)

    # Deprecated field that tracks guest users
    is_guest = models.BooleanField(default=False)

    # The mobile country code of the phone number of the user. Prefix of the number (Eg: +251 for Ethiopia)
    mobile_country_code = models.CharField(max_length=5, blank=True, null=True)
    
    # The mobile number of the user with out the country prefix number (Eg: 9876543210)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    v1_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['first_name']

# This is the model that is used to track the profile of users
class ShilengaeUserProfile(Timestampable):
    # This is the registration method the user used to sign upp
    registration_method = models.CharField(choices=REGISTRATION_METHOD, max_length=50, blank=True)
    company_name = models.CharField(max_length=50, blank=True)
    facebook_id = models.CharField(max_length=50, blank=True)
    # This field is for Admin users to view the country they have chosen to operate in and
    operating_country = models.ForeignKey(Country,
                                          related_name='+',
                                          null=True,
                                          on_delete=models.SET_NULL)

    # This field is to have the list of countries that the admin can operate in and is set by the SuperAdmin
    operable_countries = models.ManyToManyField(Country,
                                                related_name='+',
                                                blank=True)

    # This is the profile picture of the user
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)

    # This is the facebook profile of the user
    facebook_profile = models.CharField(max_length=200, blank=True)

    # This is firebase cloud message token used for chat
    fcm_token = models.CharField(max_length=200, blank=True)

    # This is the user that is associated with the profile
    user = AutoOneToOneField(ShilengaeUser, related_name="profile", on_delete=models.CASCADE)
    
    online_status = models.BooleanField(default=False)
    business_user = models.BooleanField(default=False)
    
    verified_email = models.BooleanField(default=False)
    verified_phone = models.BooleanField(default=False)
    verified_facebook = models.BooleanField(default=False)

class ShilengaeUserPreference(Timestampable):
    user = AutoOneToOneField(ShilengaeUser, related_name="preferences", on_delete=models.CASCADE)
    app_notification = models.BooleanField(default=True)
    chat_notification = models.BooleanField(default=True)

class BlacklistedToken(Timestampable):
    token = models.CharField(max_length=500, unique=True)

    @staticmethod
    def is_blacklisted(token):
        return BlacklistedToken.objects.filter(token=token).exists()
from django.db import models

from .enums import STATUS

# Create your models here.
class Timestampable(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def modified(self):
        return True if self.updated_at else False

class Activatable(models.Model):
    # The status of this city
    status = models.CharField(choices=STATUS, max_length=10, default=STATUS.ACTIVE)

    class Meta:
        abstract = True

class AppVersion(models.Model):
    app_version = models.CharField(max_length=10)
    min_android_version = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    max_android_version = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    min_ios_version = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    max_ios_version = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category_version = models.IntegerField(default=0)
    force_update = models.BooleanField(default=False)

class TermsAndConditions(Timestampable):
    # The status of this city
    title = models.CharField(max_length=100)
    content = models.TextField()

class PrivacyPolicy(Timestampable):
    title = models.CharField(max_length=100)
    content = models.TextField()

class ShilengaeIssueReport(Timestampable):
    issue_submission_url = models.URLField(max_length=500)
from django.contrib import admin

from .models import Category, FormField, FormFieldResponse
# Register your models here.

admin.site.register(Category)
admin.site.register(FormField)
admin.site.register(FormFieldResponse)
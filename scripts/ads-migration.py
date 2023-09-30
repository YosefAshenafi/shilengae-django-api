import json
from urllib.parse import urlparse
import requests
from django.core.files.base import ContentFile

from .mysqlConnection import cnx

from locations.models import Country, Region, City
from forms.models import Category, Form, FormField, FormFieldResponse, FormFieldImageResponse
from ads.models import Ad
from users.models import ShilengaeUser

ethiopia = Country.objects.filter(name='Ethiopia').first()

aa_region = Region.objects.filter(symbol='971').first()
am_region = Region.objects.filter(symbol='972').first()

aa_city = City.objects.filter(symbol='82').first()
bd_city = City.objects.filter(symbol='13').first()

root_form = Form.objects.filter(name='Root', country=ethiopia).first()
title_field = FormField.objects.filter(form=root_form, name='Title').first()
description_field = FormField.objects.filter(
    form=root_form, name='Description').first()
price_field = FormField.objects.filter(form=root_form, name='Price').first()
region_field = FormField.objects.filter(form=root_form, name='Region').first()
image_field = FormField.objects.filter(form=root_form, name='Image').first()

print(cnx)
cursor = cnx.cursor()


print(cnx)
query = ("SELECT id, cat_id, parent_cat_id, user_id, title, price, location, data FROM formvalues WHERE id > 991 LIMIT 2000")

cursor.execute(query, ())
ads = []
print(cursor)

for ad_v1 in cursor:
    ads.append(ad_v1)

for ad_v1 in ads:
    (id, cat_id, parent_cat_id, user_id, title, price, location, data) = ad_v1

    description = ''
    images = []
    for field_value in json.loads(data):
        if field_value['title'] == 'Description':
            description = field_value['value']
            break
        elif field_value['title'] == 'Pictures':
            images = field_value['value'].split(',')

    user = ShilengaeUser.objects.filter(v1_id=user_id).first()
    category = Category.objects.filter(v1_id=cat_id).first()

    try:
        if Ad.objects.filter(v1_id=id).exists():
            print("{} Skipped".format(id))
            continue
        ad = Ad()
        ad.user = user
        ad.category = category
        ad.v1_id = id
        ad.save()

        # set title
        ad_title = FormFieldResponse()
        ad_title.form_field = title_field
        ad_title.user = user
        ad_title.ad = ad
        ad_title.data = {'value': title}
        ad_title.save()

        # set description
        ad_description = FormFieldResponse()
        ad_description.form_field = description_field
        ad_description.user = user
        ad_description.ad = ad
        ad_description.data = {'value': description}
        ad_description.save()

        # set price
        ad_price = FormFieldResponse()
        ad_price.form_field = price_field
        ad_price.user = user
        ad_price.ad = ad
        ad_price.data = {}
        if price:
            ad_price.data = {'value': int(price)}
        ad_price.save()

        # # set region

        ad_region = FormFieldResponse()
        ad_region.form_field = region_field
        ad_region.user = user
        ad_region.ad = ad

        city = City.objects.filter(v1_id=location).first()

        ad_region.data = {'value': city.region.id, 'city': city.id}

        ad_region.save()

        # set image
        ad_image = FormFieldResponse()
        ad_image.form_field = image_field
        ad_image.user = user
        ad_image.ad = ad
        ad_image.data = {}
        ad_image.save()

        for image in images:
            image_response = FormFieldImageResponse()
            image_response.form_field_response = ad_image

            image_url = 'http://15.184.206.158/media/{}'.format(image)
            response = requests.get(image_url)
            if response.status_code == 200:
                image_response.image.save(image, ContentFile(response.content), save=True)


        print('{} - {} successfully migrated'.format(id, title))
    except Exception as e:
        print('{} - {} failed to migrate'.format(user_id, title))
        print(e)

print('here')
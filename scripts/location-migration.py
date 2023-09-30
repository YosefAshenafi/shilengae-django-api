from .mysqlConnection import cnx

from locations.models import Country, Region, City

ethiopia = Country.objects.filter(name='Ethiopia').first()

print(cnx)
cursor = cnx.cursor()
query = ("SELECT id, name FROM shilengae.regions WHERE country_id=63;")

cursor.execute(query, {})

for region_v1 in cursor:
    (id, name) = region_v1
    region = Region()
    region.name = name
    region.symbol = id
    region.v1_id = id
    region.country = ethiopia
    region.save()

    print('{} successfully migrated Region'.format(name))

cusror = cnx.cursor()
query = ("SELECT id, name, latitude, longitude, region_id FROM shilengae.cities WHERE country_id=63;")

cursor.execute(query, {})

for city_v1 in cursor:
    (id, name, latitude, longitude, region_id) = city_v1
    city = City()
    city.name = name
    city.symbol = id
    city.v1_id = id
    city.region = Region.objects.filter(v1_id=region_id).first()
    city.country = ethiopia
    city.save()

    print('{} successfully migrated City'.format(name))
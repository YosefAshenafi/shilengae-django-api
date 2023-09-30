from .mysqlConnection import cnx

from users.models import ShilengaeUser
from locations.models import Country

ethiopia = Country.objects.filter(name='Ethiopia').first()

print(cnx)
cursor = cnx.cursor()
query = ("SELECT id, first_name, last_name, calling_code, mobile, email, name FROM users LIMIT 1500")

cursor.execute(query, ())
for user_v1 in cursor:

    (id, first_name, last_name, calling_code, mobile, email, name) = user_v1

    user = ShilengaeUser()
    user.first_name = first_name if first_name else ''
    user.last_name = last_name
    user.mobile_country_code = calling_code
    user.mobile_number = mobile
    user.username = id
    user.email = email
    user.country = ethiopia
    user.type = ShilengaeUser.ROLE.USER
    user.v1_id = id
    user.save()

    user.profile.business_user = name != ''
    user.profile.company_name = name if name else ''
    user.profile.save()
    print("User Id", id, "migrated")

cnx.close()
# v1         -> v2
# first_name -> first_name
# last_name  -> last_name
# name -> business name
# mobile -> profile.mobile_number
# callingCode -> mobile_country_code
# email -> email
# country -> Ethiopia
# type -> USER
# created_at -> created_at
# updated_at -> updated_at

from .mysqlConnection import cnx

from users.models import ShilengaeUser
from locations.models import Country
from forms.models import Category

ethiopia = Country.objects.filter(name='Ethiopia').first()
root = Category.objects.filter(name='Root').first()

print(cnx)
cursor = cnx.cursor()
query = ("SELECT id, parent_id, name FROM categories LIMIT 1000")

cursor.execute(query, ())
for category_v1 in cursor:
    (id, parent_id, name) = category_v1
    category = Category()
    category.name = name
    category.v1_id = id
    category.country = ethiopia

    if parent_id != 0:
        parent = Category.objects.filter(v1_id=parent_id).first()
    else:
        parent = root

    category.parent = parent
    category.level = parent.level + 1

    category.save()

    category.add_self_to_parent()

    print('{} successfully migrated'.format(name))
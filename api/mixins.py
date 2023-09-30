import string, random

from .enums import STATUS
from users.models import ShilengaeUser

class GenerateDataPasswordMixin:
    def generate_user_by_phone(self, validated):
        password_requirements = string.ascii_uppercase + \
        string.ascii_lowercase + string.digits + '!#$%'
        username_requirements = string.ascii_lowercase + string.digits

        temp_password = random.sample(password_requirements, 10)
        temp_username = random.sample(username_requirements, 15)

        generated_password = "".join(temp_password)
        generated_username = "".join(temp_username)

        data = {
            # TODO: change this country to get fetched either from frontend or from where the request is coming from
            'country': 1,
            # TODO: try to fetch from these datas from the request
            'email': '',
            'first_name': generated_username,
            'last_name': '',
            'password1': generated_password,
            'password2': generated_password,
            'status': STATUS.ACTIVE,
            'type': ShilengaeUser.ROLE.USER,
            'username': generated_username,
            'firebase_uid': validated.get('uid')
        }
    
    def generate_password(self):
        password_requirements = string.ascii_uppercase + \
            string.ascii_lowercase + string.digits + '!#$%'

        temp_password = random.sample(password_requirements, 10)
        generated_password = "".join(temp_password)

        return generated_password
    
    def generate_username(self):
        username_requirements = string.ascii_lowercase + string.digits

        temp_username = random.sample(username_requirements, 15)
        generated_username = "".join(temp_username)

        return generated_username
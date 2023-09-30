from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from api.enums import STATUS
from api.test_utils import create_user_and_login
from locations.models import Country, Region, City


class UpdateUserApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, "test_username", "123456")

    def post(self, pk, body=None):
        url = reverse('users:update_user', kwargs={'pk': pk})
        return self.client.post(url, body, format="json")
    
    def test_successfully_edit_username(self):
        """
        Test if you can successfully edit username
        """
        response = self.post(self.user.id, {'username': 'new_username'})

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, 'new_username')

class SearchUserApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, "username", "password")

    def get(self, search_term):
        url = reverse('users:search_user') + "?search_term=" + search_term
        return self.client.get(url)
    
    def test_successfully_search_countries_by_user_name(self):
        """
        Test successfully search countries by user name
        """
        response = self.get('username')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.user.id)

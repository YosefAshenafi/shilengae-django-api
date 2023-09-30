from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from api.enums import STATUS
from api.test_utils import create_country, create_region, create_city, create_user_and_login
from locations.models import Country, Region, City


class CreateCountryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password', False)
        pass

    def post(self, body=None):
        url = reverse('locations:create_country')
        return self.client.post(url, body, format="json")
    
    def test_success(self):
        """
        Successfully create a country
        """
        data = {
            'currency': "ETB",
            'name': 'Ethiopia',
            'symbol': 'ETH',
            'timezone': 'East Africa Time',
            'status': STATUS.ACTIVE,
        }

        response = self.post(body=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), 1)
    
    def test_no_currency(self):
        """
        No currency input for creating a country should fail
        """
        data = {
            # 'currency': "ETB",
            'name': 'Ethiopia',
            'symbol': 'ETH',
            'timezone': 'East Africa Time',
            'status': STATUS.ACTIVE,
        }

        response = self.post(body=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Country.objects.count(), 0)
    
    def test_no_name(self):
        """
        No name input for creating a country should fail
        """
        data = {
            'currency': "ETB",
            # 'name': 'Ethiopia',
            'symbol': 'ETH',
            'timezone': 'East Africa Time',
            'status': STATUS.ACTIVE,
        }

        response = self.post(body=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Country.objects.count(), 0)
    
    def test_no_status(self):
        """
        No status input for creating a country should default to active
        """
        data = {
            'currency': "ETB",
            'name': 'Ethiopia',
            'symbol': 'ETH',
            'timezone': 'East Africa Time',
            # 'status': STATUS.ACTIVE,
        }

        response = self.post(body=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), 1)
        self.assertEqual(Country.objects.first().status, STATUS.ACTIVE)
    
    def test_no_timezone(self):
        """
        No timezone input for creating a country should default to null
        """
        data = {
            'currency': "ETB",
            'name': 'Ethiopia',
            'symbol': 'ETH',
            # 'timezone': 'East Africa Time',
            'status': STATUS.ACTIVE,
        }

        response = self.post(body=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), 1)
        self.assertEqual(Country.objects.first().timezone, None)
    
class CreateRegionApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.country = create_country("Ethiopia", "ETB", "ETH", "EAT", STATUS.ACTIVE)

    def post(self, body=None):
        url = reverse('locations:create_region')
        return self.client.post(url, body, format="json")
    
    def test_success(self):
        """
        Successfully create a region
        """
        data = {
            'name': "Oromia",
            'symbol': "OR",
            'country_id': self.country.id,
            'status': STATUS.ACTIVE
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Region.objects.count(), 1)
        self.assertEqual(Region.objects.first().name, 'Oromia')
    
    def test_no_country(self):
        """
        If there is no country provided then region creation should fail
        """
        data = {
            'name': "Oromia",
            'symbol': "OR",
            # 'country_id': self.country.id,
            'status': STATUS.ACTIVE
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Region.objects.count(), 0)

class CreateCityApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.region = create_region("test", "AM", STATUS.ACTIVE)

    def post(self, body=None):
        url = reverse('locations:create_city')
        return self.client.post(url, body, format="json")
    
    def test_success(self):
        """
        Successfully create a City
        """
        data = {
            'name': "Addis Ababa",
            'symbol': "AA",
            'region_id': self.region.id,
            'status': STATUS.ACTIVE
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(City.objects.first().name, 'Addis Ababa')
    
    def test_no_region(self):
        """
        If there is no region provided then region creation should fail
        """
        data = {
            'name': "Oromia",
            'symbol': "OR",
            # 'region_id': self.region.id,
            'status': STATUS.ACTIVE
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(City.objects.count(), 0)


class EditCountryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.country = create_country("United Arab Emirates", "ETB", "ETH", "EAT", STATUS.ACTIVE)

    def post(self, body=None):
        url = reverse('locations:edit_country')
        return self.client.post(url, body, format="json")

    def test_edit_country_name(self):
        """
        Test successfully editing a countries name
        """
        data = {
            'country_id': self.country.id,
            'name': 'Ethiopia'
        }

        response = self.post(body=data)

        self.country.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.country.name, 'Ethiopia')
    
    def test_edit_country_symbol(self):
        """
        Test successfully editing a countries symbol
        """
        data = {
            'country_id': self.country.id,
            'symbol': 'UAE'
        }

        response = self.post(body=data)

        self.country.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.country.symbol, 'UAE')
    
    def test_edit_country_status(self):
        """
        Test successfully editing countries status
        """
        data = {
            'country_id': self.country.id,
            'status': STATUS.INACTIVE,
        }

        response = self.post(body=data)

        self.country.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.country.status, STATUS.INACTIVE)

class EditRegionApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.region = create_region("test", "AM", STATUS.ACTIVE)
        self.country = create_country("United Arab Emirates", "ETB", "ETH", "EAT", STATUS.ACTIVE)


    def post(self, body=None):
        url = reverse('locations:edit_region')
        return self.client.post(url, body, format="json")

    def test_successfully_edit_region_name(self):
        """
        """
        data = {
            'region_id': self.region.id,
            'name': 'Amhara'
        }

        response = self.post(body=data)

        self.region.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.region.name, 'Amhara')
    
    def test_successfully_edit_region_symbol(self):
        """
        """
        data = {
            'region_id': self.region.id,
            'symbol': 'test'
        }

        response = self.post(body=data)

        self.region.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.region.symbol, 'test')
    
    def test_successfully_edit_region_country(self):
        """
        """
        data = {
            'region_id': self.region.id,
            'country_id': self.country.id
        }

        response = self.post(body=data)

        self.region.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.region.country.id, self.country.id)

class EditCityApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.city = create_city('test city', 'TSC', STATUS.ACTIVE)
        self.region = create_region("test", "AM", STATUS.ACTIVE)

    def post(self, body=None):
        url = reverse('locations:edit_city')
        return self.client.post(url, body, format="json")

    def test_successfully_edit_city_name(self):
        """
        """
        data = {
            'city_id': self.city.id,
            'name': "Addis Ababa"
        }

        response = self.post(body=data)

        self.city.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.city.name, 'Addis Ababa')
    
    def test_successfully_edit_city_symbol(self):
        """
        """
        data = {
            'city_id': self.city.id,
            'symbol': "NEW"
        }

        response = self.post(body=data)

        self.city.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.city.symbol, 'NEW')
    
    def test_successfully_edit_city_region(self):
        """
        """
        data = {
            'city_id': self.city.id,
            'region_id': self.region.id
        }

        response = self.post(body=data)

        self.city.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.city.region.id, self.region.id)

class ListCountryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.country = create_country("United Arab Emirates", "ETB", "ETH", "EAT", STATUS.ACTIVE)
        self.user = create_user_and_login(self, 'test_username', 'test_password', self.country)

    def get(self):
        url = reverse('locations:list_country')
        return self.client.get(url)
    
    def test_successfully_list_countries(self):
        """
        Test successfully list countries
        """
        response = self.get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.country.id)

class ListRegionApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.region = create_region("test region", "TEST", "CUR")

    def get(self):
        url = reverse('locations:list_region')
        return self.client.get(url)
    
    def test_successfully_list_countries(self):
        """
        Test successfully list countries
        """
        response = self.get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.region.id)

class ListCityApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.city = create_city("test city", "TEST", "CUR")

    def get(self):
        url = reverse('locations:list_city')
        return self.client.get(url)
    
    def test_successfully_list_countries(self):
        """
        Test successfully list countries
        """
        response = self.get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.city.id)


class SearchCountryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.country = create_country("United Arab Emirates", "ETB", "ETH", "EAT", STATUS.ACTIVE)
        self.user = create_user_and_login(self, 'test_username', 'test_password', self.country)

    def get(self, search_term):
        url = reverse('locations:search_country') + "?search_term=" + search_term
        return self.client.get(url)
    
    def test_successfully_search_countries_by_country_name(self):
        """
        Test successfully search countries by country name
        """
        response = self.get('United')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.country.id)

    def test_successfully_search_countries_by_country_symbol(self):
        """
        Test successfully search countries by their country symbol
        """
        response = self.get('ETH')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.country.id)
    
    def test_search_no_results(self):
        """
        Test if it's a not valid search term should return empty results
        """
        response = self.get('xyz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


class SearchRegionApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.region = create_region("test region", "TEST", "CUR")

    def get(self, search_term):
        url = reverse('locations:search_region') + "?search_term=" + search_term
        return self.client.get(url)
    
    def test_successfully_search_countries_by_region_name(self):
        """
        Test successfully search countries by region name
        """
        response = self.get('region')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.region.id)

    def test_successfully_search_countries_by_region_symbol(self):
        """
        Test successfully search countries by their region symbol
        """
        response = self.get('TEST')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.region.id)
    
    def test_search_no_results(self):
        """
        Test if it's a not valid search term should return empty results
        """
        response = self.get('xyz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

class SearchCityApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, 'test_username', 'test_password')
        self.city = create_city("test city", "TEST", "CUR")

    def get(self, search_term):
        url = reverse('locations:search_city') + "?search_term=" + search_term
        return self.client.get(url)
    
    def test_successfully_search_countries_by_city_name(self):
        """
        Test successfully search countries by city name
        """
        response = self.get('city')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.city.id)

    def test_successfully_search_countries_by_city_symbol(self):
        """
        Test successfully search countries by their city symbol
        """
        response = self.get('TEST')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.city.id)
    
    def test_search_no_results(self):
        """
        Test if it's a not valid search term should return empty results
        """
        response = self.get('xyz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
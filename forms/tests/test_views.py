from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from api.enums import STATUS
from api.test_utils import create_user, create_user_and_login, create_category, create_form, create_form_field
from forms.models import Category, Form, FormField


class CreateCategoryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.user = create_user_and_login(self, 'username', 'password')
        self.parent: Category = create_category("Level 1")
        self.child_1: Category = create_category("CAT1")
        self.child_1.add_parent(self.parent)
        self.form = create_form('name')

    def post(self, body=None):
        url = reverse('forms:category_create')
        return self.client.post(url, body, format='json')

    def test_success(self):
        """
        Test successfully creating a category 
        """
        data = {
            'name': 'CAT1',
            'form_id': self.form.id
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'CAT1')

    def test_children_with_different_name(self):
        """
        If two children with different names are created the request should pass
        """
        data = {
            'name': 'CAT2',
            'parent': self.parent.id,
            'form_id': self.form.id
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'CAT2')
        self.assertEqual(response.data['parent'], self.parent.id)

    def test_creating_category_with_forms_attached(self):
        """
        Test creating a category with a form attached to it
        """
        data = {
            'name': 'CAT1',
            'parent': None,
            'form_id': self.form.id,
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'CAT1')
        self.assertEqual(response.data['form'], self.form.id)

    def test_children_can_not_have_same_name(self):
        """
        If two children with the same name are trying to be created
        then request should fail.
        """
        data = {
            'name': 'CAT1',
            'parent': self.parent.id,
            'form_id': self.form.id
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchCategoryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.parent: Category = create_category("Level 1")

    def get(self, search_term):
        url = reverse('forms:category_search') + "?search_term=" + search_term
        return self.client.get(url)

    def test_successfully_search_category_by_name(self):
        """
        Test successfully search countries by country name
        """
        response = self.get('Level')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.parent.id)


class UpdateCategoryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(self, "username", "password")
        self.parent: Category = create_category("Level 1")
        self.child_1: Category = create_category("Level 2 - 1")
        self.child_2: Category = create_category("Level 2 - 2")
        self.child_3: Category = create_category("Level 3")

    def post(self, pk, body=None):
        url = reverse('forms:category_update', kwargs={'pk': pk})

        return self.client.post(url, body, format="json")

    def test_successfully_update_category_name(self):
        """
        Successfully update a category name
        """
        data = {
            'name': "new name"
        }

        response = self.post(self.parent.id, body=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.parent.refresh_from_db()

        self.assertEqual(self.parent.name, "new name")

    def test_successfully_update_category_by_attaching_children_to_parents(self):
        data = {
            'parent': self.parent.id
        }

        response = self.post(self.child_1.id, data)

        self.child_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.child_1.parent, self.parent)
        self.assertEqual(self.child_1.ancestors.first(), self.parent)
        self.assertEqual(self.parent.descendants.first(), self.child_1)

    def test_successfully_update_by_editing_ancestry(self):
        """
        Test if you can de-attach a grand_child and attach it to L1 parent
        parent                              parent                  
           |                              /        \ 
        child_2                       child_2     child_3    
           |                          
        child_3                                
        """
        self.child_2.add_parent(self.parent)
        self.child_3.add_parent(self.child_2)

        data = {
            'parent': self.parent.id
        }

        response = self.post(self.child_3.id, data)

        self.child_3.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Root parent now has 2 children
        self.assertEqual(self.parent.children.count(), 2)
        # Child 3 should only have self.parent as an ancestor because it has been detached from child_2
        self.assertEqual(self.child_3.ancestors.count(), 1)
        # Child 3 should have root parent as it's parent
        self.assertEqual(self.child_3.parent, self.parent)
        # Child 2 should have 0 children
        self.assertEqual(self.child_2.children.count(), 0)

    def test_successfully_update_by_editing_ancestry_2(self):
        """
        Test if you can de-attach a child from root parent and attach it to child_2
              parent                        parent                                                
            /        \                        |                          
        child_2     child_3       ->        child_2                          
                                              |                          
                                            child_3                                
        """
        self.child_2.add_parent(self.parent)
        self.child_3.add_parent(self.parent)

        data = {
            'parent': self.child_2.id
        }

        response = self.post(self.child_3.id, data)

        self.child_3.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Root parent now has 1 child
        self.assertEqual(self.parent.children.count(), 1)
        # Child 3 should only have self.parent as an ancestor because it has been detached from child_2
        self.assertEqual(self.child_3.ancestors.count(), 2)
        # Child 3 should have root parent as it's parent
        self.assertEqual(self.child_3.parent, self.child_2)
        # Child 2 should have 0 children
        self.assertEqual(self.child_2.children.count(), 1)


class CreateFormApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.user = create_user_and_login(self, 'username', 'password')

    def post(self, body=None):
        url = reverse('forms:form_create')
        return self.client.post(url, body, format='json')

    def test_successfully_create_form(self):
        data = {
            'name': "FORM 1"
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Form.objects.count(), 1)

    def test_successfully_create_form_with_fields(self):
        data = {
            'name': "Form 1",
            'form_fields': [
                {
                    "type": "textbox",
                    "description": "",
                    "hint": "",
                    "label": "Name",
                    "data": "{}"
                },
            ]
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Form.objects.count(), 1)
        self.assertEqual(FormField.objects.count(), 1)
        self.assertEqual(FormField.objects.first().form.id,
                         Form.objects.first().id)


class UpdateFormApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.user = create_user_and_login(self, "username", "password")
        self.form = create_form('name')

    def post(self, pk, body=None):
        url = reverse('forms:form_update', kwargs={'pk': pk})

        return self.client.post(url, body, format="json")

    def test_successfully_update_form_name(self):
        """
        Successfully update a form name
        """
        data = {
            'name': "new name"
        }

        response = self.post(self.form.id, body=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.form.refresh_from_db()

        self.assertEqual(self.form.name, "new name")

    def test_successfully_update_form_with_fields(self):
        """
        Successfully update form by adding fields
        """
        data = {
            "form_fields": [
                {
                    "type": "textbox",
                    "description": "",
                    "hint": "",
                    "label": "Name",
                    "data": "{}"
                },
            ]
        }

        response = self.post(self.form.id, body=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.form.form_fields.count(), 1)


class CreateFormFieldApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.user = create_user_and_login(self, 'username', 'password')
        self.form = create_form('name')

    def post(self, body=None):
        url = reverse('forms:form_field_create')
        return self.client.post(url, body, format='json')

    def test_successfully_create_form_field(self):
        data = {
            "type": "textbox",
            "description": "",
            "hint": "",
            "name": "",
            "label": "",
            "data": "{}",
            "is_required": False,
            "form_id": self.form.id
        }

        response = self.post(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.form.form_fields.count(), 1)


class UpdateFormFieldApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.user = create_user_and_login(self, "username", "password")
        self.form = create_form('name')
        self.form_field = create_form_field(
            "textbox",
            "test description",
            "test hint",
            "test name",
            "test label",
            0,
            self.form,
            '{}'
        )

    def post(self, pk, body=None):
        url = reverse('forms:form_field_update', kwargs={'pk': pk})

        return self.client.post(url, body, format="json")

    def test_successfully_update_form_field_label(self):
        """
        Successfully update a form name
        """
        data = {
            'label': "new label"
        }

        response = self.post(self.form_field.id, body=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.form_field.refresh_from_db()

        self.assertEqual(self.form_field.label, "new label")


class SearchFormApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')
        self.form = create_form('name')

    def get(self, search_term):
        url = reverse('forms:form_search') + "?search_term=" + search_term
        return self.client.get(url)

    def test_successfully_search_form_by_name(self):
        """
        Test successfully search forms by name
        """
        response = self.get('name')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.form.id)


class ListFormFieldByCategoryApiViewTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_user_and_login(
            self, 'test_username', 'test_password')

        self.form_1 = create_form('form1')
        self.form_field_1 = create_form_field(
            "textbox",
            "test description",
            "test hint",
            "test name",
            "test label",
            0,
            self.form_1,
            '{}'
        )

        self.form_2 = create_form('form2')
        self.form_field_2 = create_form_field(
            "textbox",
            "test description 2",
            "test hint 2",
            "test name 2",
            "test label 2",
            1,
            self.form_2,
            '{}'
        )

        self.parent: Category = create_category("Level 1")
        self.child_1: Category = create_category(
            "Level 2 - 1")
        self.child_2: Category = create_category("Level 2 - 2")
        """
        Test if you can de-attach a child from root parent and attach it to child_2
            parent
              |                          
            child_1                          
              |                          
            child_2                                
        """
        self.child_1.add_parent(self.parent)
        self.child_2.add_parent(self.child_1)

    def get(self, category_id):
        url = reverse('forms:category_fields',
                      kwargs={'pk': category_id})
        return self.client.get(url)

    def test_successfully_list_form_field_by_category(self):
        """
        Test successfully list form field by category
        """
        self.parent.form = self.form_1
        self.parent.save()

        self.child_1.form = self.form_2
        self.child_1.save()

        response = self.get(self.child_2.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'], self.form_field_1.id)
        self.assertEqual(response.data['results'][1]['id'], self.form_field_2.id)
    
    def test_successfully_list_form_field_including_self_category(self):
        """
        Test successfully list form fields by category including the leaf
        category
        """
        self.child_1.form = self.form_1
        self.child_1.save()

        self.child_2.form = self.form_2
        self.child_2.save()

        response = self.get(self.child_2.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['id'], self.form_field_1.id)
        self.assertEqual(response.data['results'][1]['id'], self.form_field_2.id)
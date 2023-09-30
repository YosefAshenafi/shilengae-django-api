from django.db.models import Q, F, Subquery, OuterRef, query, Count
from django.db import transaction
from django.db.models.aggregates import Max
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from api.models import AppVersion
from locations.models import Country

from users.models import ShilengaeUser
from api.enums import STATUS

from .serializers import CategoryIconPackSerializer, CategorySerializer, FormFieldSerializer, \
    FormSerializer, CategoryWithSubcategoriesSerializer, CategoriesWithChildrenSerializer
from .models import Category, CategoryIconPack, Form, FormField, UserCategoryFilters
from .pagination import LargeResultsSetPagination


class TestView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        data = {
            'abcd': 'test'
        }
        return Response(data, status=status.HTTP_200_OK)


class CreateCategoryApiView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        form_id = request.data.get('form_id', None)
        form = None

        if form_id:
            form = get_object_or_404(Form, pk=form_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            form=form, country=request.user.profile.operating_country)
        
        app_version = AppVersion.objects.first()
        app_version.category_version += 1
        app_version.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListCategoriesApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        filter = {}
        # check anonymous user

        if self.request.user and \
                not self.request.user.is_anonymous:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN or self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
                filter['country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['country'] = self.request.user.country

        return Category.objects.prefetch_category_data().filter(**filter)


class ListCategoriesWithSubCategoriesApiView(generics.ListAPIView):
    serializer_class = CategoryWithSubcategoriesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filter = {}

        if not self.request.user.is_anonymous:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN:
                filter['country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['country'] = self.request.user.country
        

        return Category.objects.filter(**filter)


class ListCategoriesByLevelApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.prefetch_category_data().all()

    def get_queryset(self):
        filter = {}

        if self.request.user and \
                not self.request.user.is_anonymous:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN or \
                self.request.user.type == ShilengaeUser.ROLE.SUPERADMIN:
                filter['country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['country'] = self.request.user.country

        return super().get_queryset().prefetch_category_data().filter(level=self.kwargs.get('level', None)).filter(**filter)

class ListCategoriesByLevelWithSubCategoriesApiView(ListCategoriesByLevelApiView):
    serializer_class = CategoryWithSubcategoriesSerializer

class ListCategroiesByLevelWithSubCategoriesV2ApiView(generics.ListAPIView):
    serializer_class = CategoriesWithChildrenSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        filter = {}

        if self.request.user and \
                not self.request.user.is_anonymous:
            if self.request.user.type == ShilengaeUser.ROLE.ADMIN:
                filter['country'] = self.request.user.profile.operating_country
            elif self.request.user.type == ShilengaeUser.ROLE.USER:
                filter['country'] = self.request.user.country

        return Category.objects.prefetch_category_data().filter(**filter)

class ListSelectableCategoriesApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        country = self.request.user.profile.operating_country
        filter = {}
        if self.request.user \
                and country \
                and self.request.user.type == ShilengaeUser.ROLE.ADMIN:
            filter['country'] = country
            filter['children_count'] = 0

        return super() \
            .get_queryset()\
            .annotate(children_count=Count('descendants'))\
            .filter(**filter)


class ListSubCategoriesApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        category_id = self.kwargs.get('pk', None)
        if category_id:
            return Category.objects.filter(parent=category_id, status=STATUS.ACTIVE)
        return Category.objects.none()


class UpdateCategoryApiView(generics.UpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()

    def post(self, request, *args, **kwargs):
        response = self.partial_update(request, *args, **kwargs)
        
        app_version = AppVersion.objects.first()
        app_version.category_version += 1
        app_version.save()

        return response


class DeleteCategoryApiView(generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()

    def post(self, request, *args, **kwargs):
        response = self.destroy(request, *args, **kwargs)
        
        app_version = AppVersion.objects.first()
        app_version.category_version += 1
        app_version.save()

        return response


class SearchCategoryApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        return Category.objects.filter(Q(name__icontains=search_term))


class CategoryDetailApiView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()


class CreateFormApiView(generics.CreateAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic()
    # ensures that if fields in a form are in the same position
    # to not create the form in the first place and return an
    # error message
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UpdateFormApiView(generics.UpdateAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Form.objects.all()

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DeleteFormApiView(generics.DestroyAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Form.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class DeleteBatchFormsApiView(generics.DestroyAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Form.objects.all()

    def post(self, request, *args, **kwargs):
        form_ids = request.data
        if form_ids:
            Form.objects.filter(id__in=form_ids).delete()
        return Response(status=status.HTTP_200_OK)

class DeleteFormFieldApiView(generics.DestroyAPIView):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FormField.objects.all()

    def post(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateFormFieldApiView(generics.CreateAPIView):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        form_id = request.data.get('form_id')
        form = get_object_or_404(Form, pk=form_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(form=form)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateFormFieldApiView(generics.UpdateAPIView):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FormField.objects.all()

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class SearchFormApiView(generics.ListAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_term = self.request.query_params.get('search_term')
        return Form.objects.filter(Q(name__icontains=search_term))


class ListFormApiView(generics.ListAPIView):
    serializer_class = FormSerializer
    queryset = Form.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        filter = {}
        if self.request.user and self.request.user.type == ShilengaeUser.ROLE.ADMIN:
            filter['country'] = self.request.user.profile.operating_country

        return Form.objects.filter(**filter)


class FormDetailApiView(generics.RetrieveAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Form.objects.all()


class ListFieldsByFormApiView(generics.ListAPIView):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        form_id = self.kwargs.get('pk', None)
        return FormField.objects.filter(form=form_id)


class ListFormFieldByCategoryApiView(generics.ListAPIView):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs.get('pk', None)
        is_filterable = self.request.query_params.get('is_filterable', None)
        category = get_object_or_404(Category, pk=category_id)
        # get all the forms attached to this category and it's list of ancestors field
        forms = category.get_ancestors(include_self=True).values('form')

        fields = FormField.objects\
            .filter(form__in=forms)\
            .annotate(
                level=Subquery(Category.objects.filter(id=OuterRef('form')).values('level')))\
            .order_by('name', 'type', 'level')\
            .distinct('name', 'type')
        filter = {
            'id__in': fields,
        }
        if is_filterable:
            filter['is_filterable'] = True
        
        if self.request.user.is_authenticated and self.request.user.type == ShilengaeUser.ROLE.ADMIN:
            filter['form__country'] = self.request.user.profile.operating_country

        return FormField.objects.filter(**filter).order_by('position')


class UpdateCategoryIconPackApiView(generics.UpdateAPIView):
    serializer_class = CategoryIconPackSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CategoryIconPack.objects.all()


class CreateCategoryIconApiView(generics.CreateAPIView):
    serializer_class = CategoryIconPackSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CategoryIconPack.objects.all()

    def post(self, request, *args, **kwargs):
        category = get_object_or_404(Category, pk=request.data.get('category'))
        if category.level != 2:
            raise serializers.ValidationError(
                'Only level 2 categories can have icons')

        icon = category.icon.order_by('-version').first()
        if icon:
            request.data['version'] = icon.version + 1
        return super().post(request, *args, **kwargs)


class ListCategoryIconPackApiView(generics.ListAPIView):
    serializer_class = CategoryIconPackSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # get version from query_param in the request
        version = self.request.query_params.get('version', None)
        if version:
            return self.queryset.filter(version=version)
        return CategoryIconPack.objects.all()


class ListLatestCategoryIconPackApiView(generics.CreateAPIView):
    serializer_class = CategoryIconPackSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        latest_version = CategoryIconPack.objects.aggregate(Max('version'))

        return CategoryIconPack.objects.filter(version=latest_version.get('version__max'))


class GetCategoryFilterStats(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        q = {}
        if request.query_params.get('type') == 'main':
            q['category__level'] = 2
        elif request.query_params.get('type') == 'leaf':
            q['category__descendants__isnull'] = True
        elif request.query_params.get('type') == 'node':
            q['category__descendants__count__gt'] = 0
            q['category__level__gt'] = 2

        if request.query_params.get('user'):
            q['user'] = request.query_params.get('user')

        categories = UserCategoryFilters.objects.filter(**q).values('category').annotate(total=Count('category'))

        for idx in range(len(categories)):
            category = get_object_or_404(Category, pk=categories[idx]['category'])
            categories[idx]['name'] = category.name
        
        return Response(data=categories)
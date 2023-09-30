from rest_framework import serializers

from .models import Category, Form, FormField, FormFieldImageResponse, CategoryIconPack
from .validators import image_validator
from api.enums import STATUS

import json


class FormFieldListSerializer(serializers.ListSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'type', 'description', 'hint', 'name', 'label',
                  'position', 'is_required', 'form', 'data', 'created_at']


class FormFieldSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    parsed_data = serializers.SerializerMethodField()

    class Meta:
        model = FormField
        list_serializer_class = FormFieldListSerializer
        fields = ['id', 'type', 'description', 'hint', 'name', 'label',
                  'position', 'is_required', 'form', 'data', 'parsed_data',
                  'is_filterable', 'created_at']

    def get_parsed_data(self, form_field: FormField):
        data = form_field.data
        if type(data) == str:
            data = json.loads(data)
        if form_field.type == FormField.FORM_TYPE.price and form_field.form:
            data['price_symbol'] = form_field.form.country.currency

        return data


class FormSerializer(serializers.ModelSerializer):
    form_fields = FormFieldSerializer(many=True, required=False)
    form_fields_count = serializers.SerializerMethodField()
    country = serializers.PrimaryKeyRelatedField(
        required=False, read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'name', 'form_fields', 'country',
                  'form_fields_count', 'created_at']

    def create(self, validated_data):
        fields_data = validated_data.pop('form_fields', [])
        form = Form.objects.create(**validated_data)
        self.add_fields_to_form(form, fields_data)
        self.add_country_to_form(form)
        return form

    def update(self, instance, validated_data):
        validated_field_data = validated_data.pop('form_fields', [])
        fields_data = self.initial_data['form_fields']

        for field_data in fields_data:
            if 'id' not in field_data:
                self.add_field_to_form(instance, field_data)
            else:
                if instance.form_fields.filter(position=field_data.get('position')).exclude(id=field_data.get('id')).exists():
                    raise serializers.ValidationError(
                        'Field with position {} already exists.'.format(field_data.get('position')))
                field = FormField.objects.get(id=field_data.get('id'))
                field_serializer = FormFieldSerializer(field, data=field_data)
                field_serializer.is_valid(raise_exception=True)
                field_serializer.save()

        return super().update(instance, validated_data)

    def add_fields_to_form(self, instance, fields_data):
        for field_data in fields_data:
            self.add_field_to_form(instance, field_data)

    def add_field_to_form(self, instance, field_data):
        if instance.form_fields.filter(position=field_data.get('position')).exists():
            raise serializers.ValidationError(
                'Field with position {} already exists.'.format(field_data.get('position')))

        field_serializer = FormFieldSerializer(data=field_data)
        field_serializer.is_valid(raise_exception=True)
        field = field_serializer.save(
            form=instance, data=field_data.get('data'))
        return field

    def add_country_to_form(self, instance):
        instance.country = self.context.get(
            'request').user.profile.operating_country
        instance.save()
        return instance

    def get_form_fields_count(self, obj):
        return obj.form_fields.count()

    def validate_form_fields(self, value):
        positions = set()
        for field in value:
            if field.get('position') in positions:
                raise serializers.ValidationError(
                    'Fields must have unique positions.')
            positions.add(field.get('position'))
        return value

class CategoryWithSubcategoriesSerializer(serializers.ModelSerializer):
    descendants = serializers.SerializerMethodField()
    parent_category_name = serializers.SerializerMethodField()
    parent_category_id = serializers.SerializerMethodField()
    form_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'descendants', 'parent_category_id', 'form_name', 'status', 'created_at']

    def get_descendants(self, category):
        return CategoryWithSubcategoriesSerializer(category.children, many=True).data
    
    def get_parent_category_name(self, category):
        if category.parent:
            return category.parent.name
    
    def get_parent_category_id(self, category):
        if category.parent:
            return category.parent.id

    def get_form_name(self, category):
        if category.form:
            return category.form.name


class CategoriesWithChildrenSerializer(serializers.ModelSerializer):
    form_name = serializers.SerializerMethodField()
    parent_category_id = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children', 'parent_category_id', 'form_name', 'status', 'created_at']

    def get_form_name(self, category):
        if category.form:
            return category.form.name
    
    def get_parent_category_id(self, category):
        if category.parent:
            return category.parent.id

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True)
    children = serializers.SerializerMethodField()
    form = FormSerializer
    parent_category_name = serializers.SerializerMethodField()
    form_name = serializers.SerializerMethodField()
    is_selectable = serializers.SerializerMethodField()
    descendants = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    # icon = serializers.SerializerMethodField()
    # icon_version = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'form', 'level',
                  'parent_category_name', 'form_name',
                  'descendants', 'is_selectable', 'status', 'children',
                  'country', 'created_at', 'updated_at']

    def create(self, validated_data):
        category: Category = super().create(validated_data)
        category.add_self_to_parent()
        category.form = validated_data.get('form', None)
        category.parent = validated_data.get('parent')
        if category.parent:
            category.level = category.parent.level + 1

        category.save()

        return category

    def update(self, instance: Category, validated_data):
        #    instance.add_self_to_parent()
        instance.parent = validated_data.get('parent', instance.parent)
        instance.name = validated_data.get('name', instance.name)
        instance.form = validated_data.get('form', instance.form)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        instance.add_self_to_parent()
        return instance

    def validate_name(self, value):

        invalid = Category.objects.filter(parent=self.initial_data.get(
            'parent', None), name=self.initial_data.get('name', None), country=self.context.get('request').user.profile.operating_country).exists()
        if self.instance and self.instance.name == value:
            return value
        if invalid:
            raise serializers.ValidationError(
                f"There is already a category named {self.initial_data['name']} attached to the parent.")

        return value

    def get_parent_category_name(self, category):
        if category.parent:
            return category.parent.name

    def get_form_name(self, category):
        if category.form:
            return category.form.name

    def get_is_selectable(self, category: Category):
        return category.descendants.count() == 0

    def get_icon(self, category: Category):
        obj: CategoryIconPack = category.icon.order_by('-version').first()
        if obj and category.level == 2:
            return self.context.get('request').build_absolute_uri(obj.icon.url)

    def get_icon_version(self, category: Category):
        obj: CategoryIconPack = category.icon.order_by('-version').first()
        if obj and category.level == 2:
            return obj.version

    def get_children(self, category: Category):
        return category.children.values('name')


class CategoryIconPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryIconPack
        fields = ['id', 'category', 'version',
                  'icon', 'created_at', 'updated_at']


class FormFieldImageResponseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[image_validator])
    class Meta:
        model = FormFieldImageResponse
        fields = ['id', 'form_field_response', 'image']


class FormFieldMultipleImageResponseSerializer(serializers.Serializer):
    images = serializers.ImageField(validators=[image_validator])

    class Meta:
        fields = ['images']

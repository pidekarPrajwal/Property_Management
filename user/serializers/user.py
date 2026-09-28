from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from setup.models import Area, District, Project, Region, State
from user.designations import validate_location_assignment
from user.hierarchy import (
    can_modify_area,
    can_modify_district,
    can_modify_region,
    can_modify_state,
    is_global_access,
)
from user.models import User


@extend_schema_field(OpenApiTypes.STR)
class PlaceInputField(serializers.Field):
    """A place id or its name. The response still returns the id."""

    def __init__(self, **kwargs):
        kwargs.setdefault('required', False)
        kwargs.setdefault('allow_null', True)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if data is None or data == '' or data == 0 or data == '0':
            return None
        if isinstance(data, bool):
            self.fail('invalid')
        if isinstance(data, int):
            return data
        if isinstance(data, str):
            text = data.strip()
            if text == '' or text == '0':
                return None
            return text
        self.fail('invalid')

    def to_representation(self, value):
        if value is None:
            return None
        return getattr(value, 'pk', value)


def _blank_place(value):
    return value in (None, '', 0, '0')


class _NewPlace:
    """A name that is not in the database yet. It is created only after the rest of the body is valid."""

    def __init__(self, model, name):
        self.model = model
        self.name = name


def _can_create_place(actor, model, parent):
    if actor is None or not getattr(actor, 'is_authenticated', False):
        return False
    if model is State:
        return is_global_access(actor)
    if isinstance(parent, _NewPlace):
        return is_global_access(actor)
    if parent is None:
        return False
    if model is Region:
        return can_modify_state(actor, parent)
    if model is District:
        return can_modify_region(actor, parent)
    if model is Area:
        return can_modify_district(actor, parent)
    if model is Project:
        return can_modify_area(actor, parent)
    return False


def resolve_place(model, raw, parent, parent_lookup, label, actor=None):
    """Turn an id or a name into one record. A new name is created when this account may add that place."""
    if isinstance(raw, model):
        return raw
    if _blank_place(raw):
        return None

    if isinstance(parent, _NewPlace):
        if isinstance(raw, int) or (isinstance(raw, str) and str(raw).isdigit()):
            raise serializers.ValidationError(f'No {label} with id {raw}.')
        name = str(raw).strip()
        if _can_create_place(actor, model, parent):
            return _NewPlace(model, name)
        raise serializers.ValidationError(f'No {label} named "{name}".')

    records = model.objects.all()
    scoped = records.filter(**{parent_lookup: parent}) if parent is not None and parent_lookup else records
    if isinstance(raw, int) or (isinstance(raw, str) and raw.isdigit()):
        pk = int(raw)
        found = scoped.filter(pk=pk).first()
        if found is not None:
            return found
        if records.filter(pk=pk).exists() and parent is not None:
            raise serializers.ValidationError(
                f'The selected {label} does not belong to the selected {parent_lookup}.'
            )
        raise serializers.ValidationError(f'No {label} with id {pk}.')

    name = str(raw).strip()
    matches = list(scoped.filter(name__iexact=name)[:2])
    if len(matches) == 1:
        return matches[0]
    if parent is not None and records.filter(name__iexact=name).exists():
        raise serializers.ValidationError(f'No {label} named "{name}" under the selected {parent_lookup}.')
    if len(matches) > 1:
        raise serializers.ValidationError(
            f'More than one {label} is named "{name}". Send the id instead.'
        )
    if _can_create_place(actor, model, parent):
        return _NewPlace(model, name)
    raise serializers.ValidationError(f'No {label} named "{name}".')


PLACE_CHAIN = (
    ('state', State, None, None, 'state'),
    ('region', Region, 'state', 'state', 'region'),
    ('district', District, 'region', 'region', 'district'),
    ('area', Area, 'district', 'district', 'area'),
    ('project', Project, 'area', 'area', 'project'),
)


class _UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, trim_whitespace=False)
    state_name = serializers.CharField(source='state.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    designation_label = serializers.CharField(source='get_designation_display', read_only=True)
    state = PlaceInputField(
        help_text='Required for a State Head and every head below. Send the state name, for example Maharashtra, or its id. The response state number is that id. state_name is the name.',
    )
    region = PlaceInputField(
        help_text='Required for a Region Head and every head below. Optional for a State Head. Name or id inside the selected state.',
    )
    district = PlaceInputField(
        help_text='Required for a District Head and every head below. Optional for a State Head and a Region Head.',
    )
    area = PlaceInputField(
        help_text='Required for an Area Head and a Project Head. Optional for the heads above them.',
    )
    project = PlaceInputField(
        help_text='Required only for a Project Head. Optional for every head above Project Head.',
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'mobile_number',
            'password',
            'designation',
            'designation_label',
            'state',
            'state_name',
            'region',
            'region_name',
            'district',
            'district_name',
            'area',
            'area_name',
            'project',
            'project_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True},
            'mobile_number': {'required': True},
            'designation': {'required': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None:
            self.fields['password'].required = True

    def validate(self, attrs):
        errors = {}
        password = attrs.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except DjangoValidationError as exc:
                errors['password'] = list(exc.messages)

        current = self.instance
        request = self.context.get('request')
        actor = getattr(request, 'user', None)
        designation = attrs.get('designation', getattr(current, 'designation', None))
        resolved = {}
        place_errors = {}
        for field, model, parent_field, parent_lookup, label in PLACE_CHAIN:
            raw = attrs[field] if field in attrs else getattr(current, field, None)
            if _blank_place(raw):
                resolved[field] = None
                if field in attrs:
                    attrs[field] = None
                continue
            parent = resolved.get(parent_field) if parent_field else None
            if parent_field and parent_field in place_errors:
                if not _blank_place(raw):
                    place_errors[field] = f'Select a valid {parent_field} before choosing a {label}.'
                resolved[field] = None
                continue
            try:
                resolved[field] = resolve_place(
                    model, raw, parent, parent_lookup, label, actor=actor
                )
            except serializers.ValidationError as exc:
                place_errors[field] = exc.detail[0] if isinstance(exc.detail, list) else exc.detail
                resolved[field] = None
                continue
            if field in attrs and not isinstance(resolved[field], _NewPlace):
                attrs[field] = resolved[field]
        errors.update(place_errors)
        if errors:
            raise serializers.ValidationError(errors)

        for field, model, parent_field, parent_lookup, label in PLACE_CHAIN:
            pending = resolved.get(field)
            if not isinstance(pending, _NewPlace):
                continue
            parent = resolved.get(parent_field) if parent_field else None
            created = model.objects.create(**{
                'name': pending.name,
                **({parent_lookup: parent} if parent_lookup else {}),
            })
            resolved[field] = created
            if field in attrs:
                attrs[field] = created

        try:
            validate_location_assignment(
                designation,
                resolved['state'],
                resolved['region'],
                resolved['district'],
                resolved['area'],
                resolved['project'],
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class CreateUserSerializer(_UserSerializer):
    pass


class GetUserSerializer(_UserSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False


class GetUserByIdSerializer(GetUserSerializer):
    pass


class UpdateUserSerializer(_UserSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False

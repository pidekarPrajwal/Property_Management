from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from setup.models import Area, District, Project, Region, State
from user.designations import validate_location_assignment
from user.models import User


class _UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, trim_whitespace=False)
    state_name = serializers.CharField(source='state.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    designation_label = serializers.CharField(source='get_designation_display', read_only=True)

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
            'state': {'queryset': State.objects.all(), 'required': False, 'allow_null': True},
            'region': {'queryset': Region.objects.all(), 'required': False, 'allow_null': True},
            'district': {'queryset': District.objects.all(), 'required': False, 'allow_null': True},
            'area': {'queryset': Area.objects.all(), 'required': False, 'allow_null': True},
            'project': {'queryset': Project.objects.all(), 'required': False, 'allow_null': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is None:
            self.fields['password'].required = True

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            try:
                validate_password(password, self.instance)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({'password': list(exc.messages)})

        current = self.instance
        designation = attrs.get('designation', getattr(current, 'designation', None))
        state = attrs['state'] if 'state' in attrs else getattr(current, 'state', None)
        region = attrs['region'] if 'region' in attrs else getattr(current, 'region', None)
        district = attrs['district'] if 'district' in attrs else getattr(current, 'district', None)
        area = attrs['area'] if 'area' in attrs else getattr(current, 'area', None)
        project = attrs['project'] if 'project' in attrs else getattr(current, 'project', None)

        try:
            validate_location_assignment(designation, state, region, district, area, project)
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

from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from setup.models import Site
from setup.serializers.state import _reject_duplicate


class _SiteSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    district = serializers.IntegerField(source='area.district_id', read_only=True)
    district_name = serializers.CharField(source='area.district.name', read_only=True)
    region = serializers.IntegerField(source='area.district.region_id', read_only=True)
    region_name = serializers.CharField(source='area.district.region.name', read_only=True)
    state = serializers.IntegerField(source='area.district.region.state_id', read_only=True)
    state_name = serializers.CharField(source='area.district.region.state.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'code', 'address', 'latitude', 'longitude', 'current_market_rate',
            'area', 'area_name', 'project', 'project_name',
            'district', 'district_name', 'region', 'region_name', 'state', 'state_name',
            'is_active', 'created_by', 'created_by_username', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'current_market_rate']

    def _number_list(self, value, field, low, high):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError(f'{field} must be a list of numbers.')
        numbers = []
        for index, item in enumerate(value, start=1):
            try:
                number = Decimal(str(item))
            except (InvalidOperation, TypeError, ValueError):
                raise serializers.ValidationError(f'{field} value {index} must be a number.')
            if not low <= number <= high:
                raise serializers.ValidationError(
                    f'{field} value {index} must be between {low} and {high}.'
                )
            numbers.append(float(number))
        return numbers

    def validate_latitude(self, value):
        return self._number_list(value, 'latitude', Decimal('-90'), Decimal('90'))

    def validate_longitude(self, value):
        return self._number_list(value, 'longitude', Decimal('-180'), Decimal('180'))

    def validate(self, attrs):
        latitudes = attrs.get('latitude', getattr(self.instance, 'latitude', None) or [])
        longitudes = attrs.get('longitude', getattr(self.instance, 'longitude', None) or [])
        if len(latitudes) != len(longitudes):
            raise serializers.ValidationError(
                'latitude and longitude must contain the same number of values.'
            )
        if latitudes and len(latitudes) < 3:
            raise serializers.ValidationError(
                'A site polygon needs at least 3 latitude and longitude values.'
            )
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        area = attrs.get('area', getattr(self.instance, 'area', None))
        project = attrs.get('project', getattr(self.instance, 'project', None))
        if area is None:
            raise serializers.ValidationError({'area': 'A site must belong to an area.'})
        if project is None:
            raise serializers.ValidationError({'project': 'A site must belong to a project.'})
        if project.area_id != area.id:
            raise serializers.ValidationError(
                {'project': 'The selected project does not belong to the selected area.'}
            )
        names = Site.objects.filter(project=project, name=name)
        codes = Site.objects.filter(project=project, code=code) if code else Site.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'A site with this name already exists in the selected project.')
        _reject_duplicate(codes, 'A site with this code already exists in the selected project.', 'code')
        attrs['name'] = name
        return attrs


class CreateSiteSerializer(_SiteSerializer):
    pass


class GetSiteSerializer(_SiteSerializer):
    pass


class GetSiteByIdSerializer(_SiteSerializer):
    pass


class UpdateSiteSerializer(_SiteSerializer):
    pass

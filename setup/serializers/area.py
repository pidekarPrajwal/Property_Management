from rest_framework import serializers

from setup.models import Area
from setup.serializers.state import _reject_duplicate


class _AreaSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    region = serializers.IntegerField(source='district.region_id', read_only=True)
    region_name = serializers.CharField(source='district.region.name', read_only=True)
    state = serializers.IntegerField(source='district.region.state_id', read_only=True)
    state_name = serializers.CharField(source='district.region.state.name', read_only=True)

    class Meta:
        model = Area
        fields = [
            'id', 'name', 'code', 'district', 'district_name', 'region', 'region_name',
            'state', 'state_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        district = attrs.get('district', getattr(self.instance, 'district', None))
        if district is None:
            raise serializers.ValidationError({'district': 'An area must belong to a district.'})
        names = Area.objects.filter(district=district, name=name)
        codes = Area.objects.filter(district=district, code=code) if code else Area.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'An area with this name already exists in the selected district.')
        _reject_duplicate(codes, 'An area with this code already exists in the selected district.', 'code')
        attrs['name'] = name
        return attrs


class CreateAreaSerializer(_AreaSerializer):
    pass


class GetAreaSerializer(_AreaSerializer):
    pass


class GetAreaByIdSerializer(_AreaSerializer):
    pass


class UpdateAreaSerializer(_AreaSerializer):
    pass

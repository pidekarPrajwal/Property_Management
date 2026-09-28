from rest_framework import serializers

from setup.models import District
from setup.serializers.state import _reject_duplicate


class _DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    state = serializers.IntegerField(source='region.state_id', read_only=True)
    state_name = serializers.CharField(source='region.state.name', read_only=True)

    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'region', 'region_name', 'state', 'state_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        region = attrs.get('region', getattr(self.instance, 'region', None))
        if region is None:
            raise serializers.ValidationError({'region': 'A district must belong to a region.'})
        names = District.objects.filter(region=region, name=name)
        codes = District.objects.filter(region=region, code=code) if code else District.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'A district with this name already exists in the selected region.')
        _reject_duplicate(codes, 'A district with this code already exists in the selected region.', 'code')
        attrs['name'] = name
        return attrs


class CreateDistrictSerializer(_DistrictSerializer):
    pass


class GetDistrictSerializer(_DistrictSerializer):
    pass


class GetDistrictByIdSerializer(_DistrictSerializer):
    pass


class UpdateDistrictSerializer(_DistrictSerializer):
    pass

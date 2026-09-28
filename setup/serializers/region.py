from rest_framework import serializers

from setup.models import Region
from setup.serializers.state import _reject_duplicate


class _RegionSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'state', 'state_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        state = attrs.get('state', getattr(self.instance, 'state', None))
        if state is None:
            raise serializers.ValidationError({'state': 'A region must belong to a state.'})
        names = Region.objects.filter(state=state, name=name)
        codes = Region.objects.filter(state=state, code=code) if code else Region.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'A region with this name already exists in the selected state.')
        _reject_duplicate(codes, 'A region with this code already exists in the selected state.', 'code')
        attrs['name'] = name
        return attrs


class CreateRegionSerializer(_RegionSerializer):
    pass


class GetRegionSerializer(_RegionSerializer):
    pass


class GetRegionByIdSerializer(_RegionSerializer):
    pass


class UpdateRegionSerializer(_RegionSerializer):
    pass

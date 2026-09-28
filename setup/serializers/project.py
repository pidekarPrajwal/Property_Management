from rest_framework import serializers

from setup.models import Project
from setup.serializers.state import _reject_duplicate


class _ProjectSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    district = serializers.IntegerField(source='area.district_id', read_only=True)
    district_name = serializers.CharField(source='area.district.name', read_only=True)
    region = serializers.IntegerField(source='area.district.region_id', read_only=True)
    region_name = serializers.CharField(source='area.district.region.name', read_only=True)
    state = serializers.IntegerField(source='area.district.region.state_id', read_only=True)
    state_name = serializers.CharField(source='area.district.region.state.name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'area', 'area_name', 'district', 'district_name',
            'region', 'region_name', 'state', 'state_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        area = attrs.get('area', getattr(self.instance, 'area', None))
        if area is None:
            raise serializers.ValidationError({'area': 'A project must belong to an area.'})
        names = Project.objects.filter(area=area, name=name)
        codes = Project.objects.filter(area=area, code=code) if code else Project.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'A project with this name already exists in the selected area.')
        _reject_duplicate(codes, 'A project with this code already exists in the selected area.', 'code')
        attrs['name'] = name
        return attrs


class CreateProjectSerializer(_ProjectSerializer):
    pass


class GetProjectSerializer(_ProjectSerializer):
    pass


class GetProjectByIdSerializer(_ProjectSerializer):
    pass


class UpdateProjectSerializer(_ProjectSerializer):
    pass

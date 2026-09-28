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
            'region', 'region_name', 'state', 'state_name', 'phase', 'building_type',
            'work_order_date', 'expected_end_date', 'contractor', 'latest_progress',
            'created_at', 'updated_at',
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
        building_type = attrs.get('building_type', getattr(self.instance, 'building_type', []))
        if building_type in (None, ''):
            building_type = []
        if not isinstance(building_type, list) or not all(isinstance(item, str) for item in building_type):
            raise serializers.ValidationError({'building_type': 'Send a list of names, for example Residential.'})
        progress = attrs.get('latest_progress', getattr(self.instance, 'latest_progress', None))
        if progress == '':
            progress = None
        if progress is not None and not isinstance(progress, dict):
            raise serializers.ValidationError(
                {'latest_progress': 'Send an object with entry_time, physical_progress_percent, and description.'}
            )
        attrs['name'] = name
        attrs['building_type'] = building_type
        if 'latest_progress' in attrs:
            attrs['latest_progress'] = progress
        return attrs


class CreateProjectSerializer(_ProjectSerializer):
    pass


class GetProjectSerializer(_ProjectSerializer):
    pass


class GetProjectByIdSerializer(_ProjectSerializer):
    pass


class UpdateProjectSerializer(_ProjectSerializer):
    pass


def _plain_coordinate(value):
    text = format(value, 'f').rstrip('0').rstrip('.')
    return text or '0'


class ProjectForMapSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_code = serializers.CharField(source='code', allow_blank=True)
    title = serializers.CharField(source='name')
    site_location = serializers.SerializerMethodField()
    phase = serializers.SerializerMethodField()
    building_type = serializers.SerializerMethodField()
    latest_progress = serializers.JSONField()
    work_order_date = serializers.DateField(allow_null=True)
    expected_end_date = serializers.DateField(allow_null=True)
    contractor = serializers.SerializerMethodField()

    def get_site_location(self, project):
        for site in project.sites.all():
            if site.latitude is None or site.longitude is None:
                continue
            return f'{_plain_coordinate(site.latitude)}, {_plain_coordinate(site.longitude)}'
        return None

    def get_phase(self, project):
        return project.phase or None

    def get_building_type(self, project):
        return project.building_type or []

    def get_contractor(self, project):
        return project.contractor or None

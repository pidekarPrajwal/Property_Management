from rest_framework import serializers

from setup.models import State


def _reject_duplicate(queryset, message, field='name'):
    if queryset.exists():
        raise serializers.ValidationError({field: message})


class _StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        return value.strip()

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', '')).strip()
        code = attrs.get('code', getattr(self.instance, 'code', ''))
        names = State.objects.filter(name=name)
        codes = State.objects.filter(code=code) if code else State.objects.none()
        if self.instance is not None:
            names = names.exclude(pk=self.instance.pk)
            codes = codes.exclude(pk=self.instance.pk)
        _reject_duplicate(names, 'A state with this name already exists.')
        _reject_duplicate(codes, 'A state with this code already exists.', 'code')
        attrs['name'] = name
        return attrs


class CreateStateSerializer(_StateSerializer):
    pass


class GetStateSerializer(_StateSerializer):
    pass


class GetStateByIdSerializer(_StateSerializer):
    pass


class UpdateStateSerializer(_StateSerializer):
    pass

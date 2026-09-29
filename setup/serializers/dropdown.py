from rest_framework import serializers


class DropdownOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

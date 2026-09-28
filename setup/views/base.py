from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response


def id_filter(queryset, param, raw_value, lookup):
    if raw_value in (None, ''):
        return queryset
    if not str(raw_value).isdigit():
        raise ValidationError({param: 'Enter a valid id.'})
    return queryset.filter(**{lookup: int(raw_value)})


class RecordViewSet(viewsets.ModelViewSet):
    """Shared list, detail, update and delete steps. Each module names its own actions."""

    read_serializer_class = None
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def object_by_id(self):
        raw = self.request.query_params.get('id')
        if raw in (None, '') and hasattr(self.request, 'data'):
            raw = self.request.data.get('id')
        if raw in (None, ''):
            raise ValidationError({'id': 'Pass id as ?id= or in the request body.'})
        if not str(raw).isdigit():
            raise ValidationError({'id': 'Enter a valid id.'})
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=int(raw))
        except queryset.model.DoesNotExist:
            raise NotFound()

    def create_record(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = self.read_serializer_class(serializer.instance, context=self.get_serializer_context())
        return Response(output.data, status=status.HTTP_201_CREATED)

    def list_records(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def record_by_id(self, request):
        serializer = self.get_serializer(self.object_by_id())
        return Response(serializer.data)

    def update_record(self, request):
        instance = self.object_by_id()
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        output = self.read_serializer_class(serializer.instance, context=self.get_serializer_context())
        return Response(output.data)

    def delete_record(self, request):
        instance = self.object_by_id()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HierarchyViewSet(RecordViewSet):
    def get_queryset(self):
        from user.hierarchy import visible_queryset

        queryset = visible_queryset(self.request.user, super().get_queryset())
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return self.apply_filters(queryset)

    def apply_filters(self, queryset):
        return queryset

    def perform_destroy(self, instance):
        self.ensure_can_change(instance)
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {
                    'detail': (
                        'This record cannot be deleted because other records still use it. '
                        'Remove or move those records first.'
                    )
                }
            )

    def ensure_can_change(self, instance):
        raise NotImplementedError

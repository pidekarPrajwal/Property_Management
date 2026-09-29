from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class State(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                condition=~models.Q(code=''),
                name='unique_state_code_when_set',
            ),
        ]

    def __str__(self):
        return self.name


class Region(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True, default='')
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='regions')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['state', 'name'], name='unique_region_name_per_state'),
            models.UniqueConstraint(
                fields=['state', 'code'],
                condition=~models.Q(code=''),
                name='unique_region_code_per_state',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.state})'


class District(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True, default='')
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='districts')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'name'],
                name='unique_district_name_per_region',
            ),
            models.UniqueConstraint(
                fields=['region', 'code'],
                condition=~models.Q(code=''),
                name='unique_district_code_per_region',
            ),
        ]

    def __str__(self):
        return self.name


class Area(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True, default='')
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='areas')

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['district', 'name'], name='unique_area_name_per_district'),
            models.UniqueConstraint(
                fields=['district', 'code'],
                condition=~models.Q(code=''),
                name='unique_area_code_per_district',
            ),
        ]

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True, default='')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='projects')
    phase = models.CharField(max_length=40, blank=True, default='')
    building_type = models.JSONField(default=list, blank=True)
    work_order_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    contractor = models.CharField(max_length=255, blank=True, default='')
    latest_progress = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['area', 'name'], name='unique_project_name_per_area'),
            models.UniqueConstraint(
                fields=['area', 'code'],
                condition=~models.Q(code=''),
                name='unique_project_code_per_area',
            ),
        ]

    def __str__(self):
        return self.name


class Site(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    latitude = models.JSONField(default=list, blank=True)
    longitude = models.JSONField(default=list, blank=True)
    current_market_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='sites')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='sites')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_sites',
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['project', 'name'], name='unique_site_name_per_project'),
            models.UniqueConstraint(
                fields=['project', 'code'],
                condition=~models.Q(code=''),
                name='unique_site_code_per_project',
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.area_id and self.project_id and self.project.area_id != self.area_id:
            raise ValidationError(
                {'project': 'The selected project does not belong to the selected area.'}
            )

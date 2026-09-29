from django.db import models


class Property(models.Model):
    """One property. XLSX sync updates only columns present in that file."""

    property_id = models.CharField(max_length=64, unique=True)
    address = models.TextField(blank=True, default='')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    area_sqft = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    market_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    current_market_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    owner_name = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=40, blank=True, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['property_id']
        verbose_name_plural = 'properties'

    def __str__(self):
        return self.property_id


class PropertySyncLog(models.Model):
    """Written only when the upload endpoint runs a real sync, not on import."""

    filename = models.CharField(max_length=255)
    synced_at = models.DateTimeField(auto_now_add=True)
    inserted = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    skipped = models.PositiveIntegerField(default=0)
    failed = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-synced_at']

class EasrRecord(models.Model):
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    vibhag_number = models.CharField(max_length=20)
    property_type = models.CharField(max_length=100)
    assessment_range = models.CharField(max_length=100)
    rate_rs = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('district', 'taluka', 'village', 'year', 'vibhag_number', 'property_type', 'assessment_range', 'unit')
        indexes = [
            models.Index(fields=['district', 'taluka', 'village'])
        ]

"""Comparable market rate. Importing this module does not change the database.

Call calculate_current_market_rates from the management command or
POST /api/properties/calculate-market-rate. The XLSX upload does not call it.
"""

from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.db import transaction

from properties.models import Property

DEFAULT_RADIUS_KM = 2


def _radius_km(radius_km):
    if radius_km is not None:
        return Decimal(str(radius_km))
    return Decimal(str(getattr(settings, 'PROPERTY_MARKET_RADIUS_KM', DEFAULT_RADIUS_KM)))


def _distance_km(left_lat, left_lng, right_lat, right_lng):
    earth_km = 6371
    lat1, lng1, lat2, lng2 = (radians(float(value)) for value in (left_lat, left_lng, right_lat, right_lng))
    delta_lat = lat2 - lat1
    delta_lng = lng2 - lng1
    arc = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lng / 2) ** 2
    return 2 * earth_km * asin(sqrt(arc))


def calculate_current_market_rates(radius_km=None):
    """Set current_market_rate from nearby properties' market_rate. Nothing else changes."""
    radius = float(_radius_km(radius_km))
    properties = list(
        Property.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    )
    updated = 0
    with transaction.atomic():
        for current in properties:
            comparables = []
            for other in properties:
                if other.pk == current.pk or other.market_rate is None:
                    continue
                distance = _distance_km(
                    current.latitude, current.longitude, other.latitude, other.longitude
                )
                if distance <= radius:
                    comparables.append(other.market_rate)
            if not comparables:
                continue
            average = sum(comparables) / Decimal(len(comparables))
            Property.objects.filter(pk=current.pk).update(current_market_rate=average)
            updated += 1
    return {'success': True, 'updated': updated, 'radius_km': radius}

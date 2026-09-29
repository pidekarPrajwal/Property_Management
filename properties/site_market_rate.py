"""Map each Site to the nearest Property market rate.

Importing this module does not read or write the database.
Call map_site_market_rates only from a management command.
"""

from decimal import Decimal

from properties.market_rate import _distance_km, _radius_km
from properties.models import Property
from setup.models import Site


def _site_point(site):
    """Centre of the stored latitude and longitude lists."""
    latitudes = site.latitude or []
    longitudes = site.longitude or []
    if not latitudes or not longitudes or len(latitudes) != len(longitudes):
        return None
    try:
        latitude = sum(Decimal(str(value)) for value in latitudes) / Decimal(len(latitudes))
        longitude = sum(Decimal(str(value)) for value in longitudes) / Decimal(len(longitudes))
    except (ArithmeticError, TypeError, ValueError):
        return None
    return latitude, longitude


def _nearest_property(point, properties, radius_km):
    latitude, longitude = point
    nearest = None
    nearest_distance = None
    for record in properties:
        distance = _distance_km(latitude, longitude, record.latitude, record.longitude)
        if distance > radius_km:
            continue
        if nearest is None or distance < nearest_distance or (
            distance == nearest_distance and record.property_id < nearest.property_id
        ):
            nearest = record
            nearest_distance = distance
    return nearest, nearest_distance


def map_site_market_rates(radius_km=None):
    """Copy Property.current_market_rate onto each nearby Site. Leaves a site unchanged when none match."""
    radius = float(_radius_km(radius_km))
    properties = list(
        Property.objects.exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .exclude(current_market_rate__isnull=True)
        .order_by('property_id')
    )
    results = []
    updated = skipped = failed = 0
    sites = Site.objects.all().order_by('name', 'id')
    for site in sites:
        try:
            point = _site_point(site)
            if point is None:
                skipped += 1
                results.append({
                    'name': site.name,
                    'location': None,
                    'matched': None,
                    'distance': None,
                    'rate': None,
                    'status': 'Skipped',
                    'reason': 'No latitude/longitude stored on this site',
                })
                continue
            match, distance = _nearest_property(point, properties, radius)
            if match is None or match.current_market_rate is None:
                skipped += 1
                results.append({
                    'name': site.name,
                    'location': point,
                    'matched': None,
                    'distance': None,
                    'rate': None,
                    'status': 'Skipped',
                    'reason': 'No nearby record found',
                })
                continue
            Site.objects.filter(pk=site.pk).update(current_market_rate=match.current_market_rate)
            updated += 1
            results.append({
                'name': site.name,
                'location': point,
                'matched': match.address.strip() or match.property_id,
                'distance': distance,
                'rate': match.current_market_rate,
                'status': 'Updated',
                'reason': '',
            })
        except Exception:
            failed += 1
            results.append({
                'name': site.name,
                'location': None,
                'matched': None,
                'distance': None,
                'rate': None,
                'status': 'Failed',
                'reason': 'Could not map this site',
            })
    return {
        'radius_km': radius,
        'results': results,
        'total': len(results),
        'updated': updated,
        'skipped': skipped,
        'failed': failed,
    }


def _place(point):
    if point is None:
        return 'Not stored'
    latitude, longitude = point
    return f'{latitude:.4f}, {longitude:.4f}'


def _rate_text(rate):
    text = format(rate, 'f').rstrip('0').rstrip('.')
    return f'₹{text}/sq.ft'


def write_report(stdout, heading, summary):
    stdout.write(heading)
    stdout.write('')
    for row in summary['results']:
        stdout.write(f"Site: {row['name']}")
        stdout.write(f"Location: {_place(row['location'])}")
        if row['status'] == 'Updated':
            stdout.write(f"Matched Location: {row['matched']}")
            stdout.write(f"Distance: {row['distance']:.2f} km")
            stdout.write(f"Current Market Rate: {_rate_text(row['rate'])}")
        else:
            stdout.write(f"Matched Location: {row['reason']}")
        stdout.write(f"Status: {row['status']}")
        stdout.write('')
    stdout.write('--------------------------------')
    stdout.write(f"Total Sites: {summary['total']}")
    stdout.write(f"Updated: {summary['updated']}")
    stdout.write(f"Skipped: {summary['skipped']}")
    stdout.write(f"Failed: {summary['failed']}")
    stdout.write('--------------------------------')
    stdout.write(f"Range: {summary['radius_km']} km")

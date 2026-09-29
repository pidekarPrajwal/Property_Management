from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from setup.models import Area, District, Project, Region, Site, State
from user.designations import Designation

User = get_user_model()

# Six revenue divisions and the 36 districts, using the current official names
# Ahilyanagar, Chhatrapati Sambhajinagar, and Dharashiv. Each district is stored
# with its real headquarters town. Coordinates are the published town centre.
# The polygon is a small box around that centre so latitude and longitude are lists.
MAHARASHTRA = {
    'Konkan': {
        'Mumbai City': ('Mumbai', 18.9388, 72.8354),
        'Mumbai Suburban': ('Bandra', 19.0544, 72.8406),
        'Thane': ('Thane', 19.2183, 72.9781),
        'Palghar': ('Palghar', 19.6967, 72.7654),
        'Raigad': ('Alibag', 18.6414, 72.8722),
        'Ratnagiri': ('Ratnagiri', 16.9902, 73.3120),
        'Sindhudurg': ('Oros', 16.1089, 73.6908),
    },
    'Pune': {
        'Pune': ('Pune', 18.5204, 73.8567),
        'Satara': ('Satara', 17.6805, 74.0183),
        'Sangli': ('Sangli', 16.8524, 74.5815),
        'Solapur': ('Solapur', 17.6599, 75.9064),
        'Kolhapur': ('Kolhapur', 16.7050, 74.2433),
    },
    'Nashik': {
        'Nashik': ('Nashik', 19.9975, 73.7898),
        'Ahilyanagar': ('Ahilyanagar', 19.0952, 74.7496),
        'Dhule': ('Dhule', 20.9042, 74.7749),
        'Jalgaon': ('Jalgaon', 21.0077, 75.5626),
        'Nandurbar': ('Nandurbar', 21.3700, 74.2400),
    },
    'Chhatrapati Sambhajinagar': {
        'Chhatrapati Sambhajinagar': ('Chhatrapati Sambhajinagar', 19.8762, 75.3433),
        'Jalna': ('Jalna', 19.8410, 75.8860),
        'Beed': ('Beed', 18.9891, 75.7601),
        'Latur': ('Latur', 18.4088, 76.5604),
        'Dharashiv': ('Dharashiv', 18.1861, 76.0421),
        'Parbhani': ('Parbhani', 19.2704, 76.7769),
        'Hingoli': ('Hingoli', 19.7173, 77.1489),
        'Nanded': ('Nanded', 19.1383, 77.3210),
    },
    'Amravati': {
        'Amravati': ('Amravati', 20.9374, 77.7796),
        'Akola': ('Akola', 20.7002, 77.0082),
        'Buldhana': ('Buldhana', 20.5293, 76.1842),
        'Yavatmal': ('Yavatmal', 20.3888, 78.1204),
        'Washim': ('Washim', 20.1119, 77.1330),
    },
    'Nagpur': {
        'Nagpur': ('Nagpur', 21.1458, 79.0882),
        'Wardha': ('Wardha', 20.7453, 78.6022),
        'Bhandara': ('Bhandara', 21.1667, 79.6500),
        'Gondia': ('Gondia', 21.4600, 80.1920),
        'Chandrapur': ('Chandrapur', 19.9615, 79.2961),
        'Gadchiroli': ('Gadchiroli', 20.1809, 80.0030),
    },
}


class Command(BaseCommand):
    help = 'Keep only real Maharashtra divisions, districts, and headquarters towns.'

    @transaction.atomic
    def handle(self, *args, **options):
        self._clear_other_data()
        state, _ = State.objects.get_or_create(name='Maharashtra', defaults={'code': 'MH'})
        if state.code != 'MH':
            state.code = 'MH'
            state.save(update_fields=['code'])

        for division, districts in MAHARASHTRA.items():
            region, _ = Region.objects.get_or_create(state=state, name=division, defaults={'code': ''})
            for district_name, (town, latitude, longitude) in districts.items():
                district, _ = District.objects.get_or_create(
                    region=region, name=district_name, defaults={'code': ''}
                )
                area, _ = Area.objects.get_or_create(
                    district=district, name=town, defaults={'code': ''}
                )
                project, _ = Project.objects.get_or_create(
                    area=area,
                    name=town,
                    defaults={
                        'code': '',
                        'phase': '',
                        'building_type': [],
                        'contractor': '',
                        'latest_progress': None,
                    },
                )
                latitudes, longitudes = _polygon(latitude, longitude)
                site, created = Site.objects.get_or_create(
                    project=project,
                    name=town,
                    defaults={
                        'code': '',
                        'address': f'{town}, {district_name}, Maharashtra',
                        'latitude': latitudes,
                        'longitude': longitudes,
                        'area': area,
                        'is_active': True,
                        'created_by': None,
                    },
                )
                if not created:
                    site.address = f'{town}, {district_name}, Maharashtra'
                    site.latitude = latitudes
                    site.longitude = longitudes
                    site.area = area
                    site.save(update_fields=['address', 'latitude', 'longitude', 'area'])

        self.stdout.write(self.style.SUCCESS(
            'Only Maharashtra remains: 6 divisions, 36 districts, and their real headquarters.'
        ))

    def _clear_other_data(self):
        Site.objects.all().delete()
        User.objects.exclude(designation=Designation.CMD).delete()
        Project.objects.all().delete()
        Area.objects.all().delete()
        District.objects.all().delete()
        Region.objects.all().delete()
        State.objects.exclude(name='Maharashtra').delete()


def _polygon(latitude, longitude, span=0.01):
    return (
        [
            round(latitude - span, 4),
            round(latitude - span, 4),
            round(latitude + span, 4),
            round(latitude + span, 4),
        ],
        [
            round(longitude - span, 4),
            round(longitude + span, 4),
            round(longitude + span, 4),
            round(longitude - span, 4),
        ],
    )

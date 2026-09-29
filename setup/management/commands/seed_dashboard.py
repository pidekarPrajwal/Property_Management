from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from setup.models import Area, District, Project, Region, Site, State
from user.designations import Designation

User = get_user_model()
PASSWORD = 'Head@12345'


class Command(BaseCommand):
    help = 'Add a small Maharashtra set so the dashboard lists have data to show.'

    @transaction.atomic
    def handle(self, *args, **options):
        state, _ = State.objects.get_or_create(
            name='Maharashtra',
            defaults={'code': 'MH'},
        )

        mumbai = _region(state, 'Mumbai', 'MH')
        pune_region = _region(state, 'Pune', 'PUN')
        nashik_region = _region(state, 'Nashik', 'NAS')
        nagpur_region = _region(state, 'Nagpur', 'NAG')

        mumbai_city = _district(mumbai, 'Mumbai City', 'MC')
        pune = _district(pune_region, 'Pune', 'PUN')
        nashik = _district(nashik_region, 'Nashik', 'NAS')
        nagpur = _district(nagpur_region, 'Nagpur', 'NAG')

        andheri = _area(mumbai_city, 'Andheri', 'AND')
        shivajinagar = _area(pune, 'Shivajinagar', 'SHV')
        kothrud = _area(pune, 'Kothrud', 'KOT')
        nashik_road = _area(nashik, 'Nashik Road', 'NSR')
        sitabuldi = _area(nagpur, 'Sitabuldi', 'SIT')

        andheri_housing = _project(
            andheri, 'Andheri Housing', 'AH', 'Phase 2', ['Residential'], 'Skyline Builders'
        )
        shivaji_housing = _project(
            shivajinagar, 'Shivajinagar Homes', 'SH', 'Phase 1', ['Residential'], 'Western Infra'
        )
        kothrud_works = _project(
            kothrud, 'Kothrud Works', 'KW', 'Phase 1', ['Commercial'], 'Deccan Contractors'
        )
        nashik_yard = _project(
            nashik_road, 'Nashik Road Yard', 'NY', 'Phase 3', ['Industrial'], 'Godavari Works'
        )
        sitabuldi_block = _project(
            sitabuldi, 'Sitabuldi Block', 'SB', 'Phase 1', ['Residential', 'Commercial'], 'Orange City Build'
        )

        thane_region = _region(state, 'Thane', 'THN')
        kolhapur_region = _region(state, 'Kolhapur', 'KOP')
        sambhaji_region = _region(state, 'Sambhajinagar', 'SAM')
        amravati_region = _region(state, 'Amravati', 'AMT')
        _region(state, 'Konkan', 'KON')

        thane = _district(thane_region, 'Thane', 'THN')
        kolhapur = _district(kolhapur_region, 'Kolhapur', 'KOP')
        sambhaji = _district(sambhaji_region, 'Sambhajinagar', 'SAM')
        amravati = _district(amravati_region, 'Amravati', 'AMT')

        thane_west = _area(thane, 'Thane West', 'THW')
        kolhapur_city = _area(kolhapur, 'Kolhapur City', 'KLC')
        cidco = _area(sambhaji, 'Cidco', 'CID')
        amravati_camp = _area(amravati, 'Amravati Camp', 'AMC')

        thane_homes = _project(
            thane_west, 'Thane West Homes', 'TWH', 'Phase 1', ['Residential'], 'Creekline Builders'
        )
        kolhapur_market = _project(
            kolhapur_city, 'Kolhapur Market', 'KLM', 'Phase 2', ['Commercial'], 'Rankala Works'
        )
        cidco_homes = _project(
            cidco, 'Cidco Homes', 'CDH', 'Phase 1', ['Residential'], 'Marathwada Infra'
        )
        camp_block = _project(
            amravati_camp, 'Camp Block', 'CMB', 'Phase 1', ['Residential'], 'Vidarbha Build'
        )

        andheri_head = _user(
            'andheri_area_head', 'Rohan', 'Patil', 'andheri.area@example.com', '9100000004',
            Designation.AREA_HEAD, state, mumbai, mumbai_city, andheri, None,
        )
        shivaji_head = _user(
            'shivajinagar_area_head', 'Neha', 'Kulkarni', 'shivaji.area@example.com', '9100000005',
            Designation.AREA_HEAD, state, pune_region, pune, shivajinagar, None,
        )
        kothrud_head = _user(
            'kothrud_area_head', 'Sonal', 'Jadhav', 'kothrud.area@example.com', '9100000007',
            Designation.AREA_HEAD, state, pune_region, pune, kothrud, None,
        )
        nashik_head = _user(
            'nashik_area_head', 'Vikas', 'Pawar', 'nashik.area@example.com', '9100000008',
            Designation.AREA_HEAD, state, nashik_region, nashik, nashik_road, None,
        )
        sitabuldi_head = _user(
            'sitabuldi_area_head', 'Priya', 'Borkar', 'sitabuldi.area@example.com', '9100000009',
            Designation.AREA_HEAD, state, nagpur_region, nagpur, sitabuldi, None,
        )

        _site(
            andheri_housing, andheri, andheri_head,
            'Andheri East Plot', 'AE1', 'Andheri East, Mumbai',
            _polygon(19.1136, 72.8697),
        )
        _site(
            andheri_housing, andheri, andheri_head,
            'Andheri West Plot', 'AW1', 'Andheri West, Mumbai',
            _polygon(19.1364, 72.8296),
        )
        _site(
            shivaji_housing, shivajinagar, shivaji_head,
            'JM Road Site', 'JM1', 'Jangli Maharaj Road, Pune',
            _polygon(18.5236, 73.8478),
        )
        _site(
            kothrud_works, kothrud, kothrud_head,
            'Kothrud Depot', 'KD1', 'Paud Road, Kothrud, Pune',
            _polygon(18.5074, 73.8077),
        )
        _site(
            nashik_yard, nashik_road, nashik_head,
            'Nashik Road Yard', 'NR1', 'Nashik Road, Nashik',
            _polygon(19.9490, 73.8390),
        )
        _site(
            sitabuldi_block, sitabuldi, sitabuldi_head,
            'Sitabuldi Square', 'SQ1', 'Sitabuldi, Nagpur',
            _polygon(21.1458, 79.0882),
        )
        _site(
            thane_homes, thane_west, None,
            'Thane West Plot', 'TW1', 'Ghodbunder Road, Thane',
            _polygon(19.2183, 72.9781),
        )
        _site(
            kolhapur_market, kolhapur_city, None,
            'Rankala Plot', 'RK1', 'Rankala Lake, Kolhapur',
            _polygon(16.6913, 74.2115),
        )
        _site(
            cidco_homes, cidco, None,
            'Cidco Plot', 'CD1', 'Cidco, Sambhajinagar',
            _polygon(19.8762, 75.3433),
        )
        _site(
            camp_block, amravati_camp, None,
            'Camp Plot', 'CP1', 'Camp, Amravati',
            _polygon(20.9374, 77.7796),
        )

        _user(
            'mh_state_head', 'Ravi', 'Deshmukh', 'ravi.state@example.com', '9100000001',
            Designation.STATE_HEAD, state, None, None, None, None,
        )
        _user(
            'pune_region_head', 'Meera', 'Joshi', 'meera.region@example.com', '9100000002',
            Designation.REGION_HEAD, state, pune_region, None, None, None,
        )
        _user(
            'pune_district_head', 'Amit', 'Shinde', 'amit.district@example.com', '9100000003',
            Designation.DISTRICT_HEAD, state, pune_region, pune, None, None,
        )
        _user(
            'shivaji_project_head', 'Kiran', 'More', 'kiran.project@example.com', '9100000006',
            Designation.PROJECT_HEAD, state, pune_region, pune, shivajinagar, shivaji_housing,
        )

        self.stdout.write(self.style.SUCCESS(
            'Dashboard sample data is ready. New head passwords are Head@12345.'
        ))


def _region(state, name, code):
    region, _ = Region.objects.get_or_create(
        state=state, name=name, defaults={'code': code}
    )
    return region


def _district(region, name, code):
    district, _ = District.objects.get_or_create(
        region=region, name=name, defaults={'code': code}
    )
    return district


def _area(district, name, code):
    area, _ = Area.objects.get_or_create(
        district=district, name=name, defaults={'code': code}
    )
    return area


def _project(area, name, code, phase, building_type, contractor):
    project, _ = Project.objects.get_or_create(
        area=area,
        name=name,
        defaults={
            'code': code,
            'phase': phase,
            'building_type': building_type,
            'work_order_date': date(2026, 1, 15),
            'expected_end_date': date(2027, 6, 30),
            'contractor': contractor,
            'latest_progress': {
                'entry_time': '2026-09-01T10:00:00Z',
                'physical_progress_percent': 35,
                'description': 'Foundation work is in progress.',
            },
        },
    )
    return project


def _polygon(latitude, longitude, span=0.004):
    return [
        {'latitude': round(latitude - span, 6), 'longitude': round(longitude - span, 6)},
        {'latitude': round(latitude - span, 6), 'longitude': round(longitude + span, 6)},
        {'latitude': round(latitude + span, 6), 'longitude': round(longitude + span, 6)},
        {'latitude': round(latitude + span, 6), 'longitude': round(longitude - span, 6)},
    ]


def _site(project, area, created_by, name, code, address, coordinates):
    site, created = Site.objects.get_or_create(
        project=project,
        name=name,
        defaults={
            'code': code,
            'address': address,
            'coordinates': coordinates,
            'area': area,
            'is_active': True,
            'created_by': created_by,
        },
    )
    if not created:
        site.coordinates = coordinates
        site.address = address
        site.area = area
        if created_by is not None:
            site.created_by = created_by
        site.save(update_fields=['coordinates', 'address', 'area', 'created_by'])


def _user(username, first_name, last_name, email, mobile, designation, state, region, district, area, project):
    user = User.objects.filter(username=username).first()
    if user is not None:
        return user
    return User.objects.create_user(
        username=username,
        email=email,
        password=PASSWORD,
        first_name=first_name,
        last_name=last_name,
        mobile_number=mobile,
        designation=designation,
        state=state,
        region=region,
        district=district,
        area=area,
        project=project,
        is_active=True,
    )

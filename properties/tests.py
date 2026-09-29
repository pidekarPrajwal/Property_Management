from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from openpyxl import Workbook
from rest_framework.test import APIClient
from django.test import TestCase

from properties.models import Property

User = get_user_model()


def workbook(headers, rows):
    book = Workbook()
    sheet = book.active
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    payload = BytesIO()
    book.save(payload)
    payload.seek(0)
    payload.name = 'properties.xlsx'
    return payload


class PropertyXlsxSyncTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='property_admin',
            email='property.admin@example.com',
            password='Head@12345',
            first_name='Property',
            last_name='Admin',
            mobile_number='9100000099',
            designation='CMD',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def upload(self, payload, dry_run=False):
        url = '/api/properties/upload-xlsx/'
        if dry_run:
            url += '?dry_run=true'
        payload.seek(0)
        return self.client.post(url, {'file': payload}, format='multipart')

    def test_second_upload_replaces_only_xlsx_columns(self):
        first = workbook(
            ['property_id', 'address', 'latitude', 'longitude', 'area_sqft', 'market_rate'],
            [[1001, 'Andheri East', 19.1197, 72.8468, 1000, 2500]],
        )
        response = self.upload(first)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['inserted'], 1)
        record = Property.objects.get(property_id='1001')
        record.owner_name = 'Existing Owner'
        record.current_market_rate = Decimal('2600')
        record.status = 'held'
        record.save(update_fields=['owner_name', 'current_market_rate', 'status'])
        untouched_updated_at = Property.objects.get(property_id='1001').updated_at

        second = workbook(
            ['property_id', 'area_sqft', 'market_rate'],
            [[1001, 1200, 2800]],
        )
        response = self.upload(second)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['updated'], 1)
        record.refresh_from_db()
        self.assertEqual(record.area_sqft, Decimal('1200.00'))
        self.assertEqual(record.market_rate, Decimal('2800.00'))
        self.assertEqual(record.owner_name, 'Existing Owner')
        self.assertEqual(record.current_market_rate, Decimal('2600.00'))
        self.assertEqual(record.status, 'held')
        self.assertEqual(record.address, 'Andheri East')
        self.assertEqual(record.updated_at, untouched_updated_at)

    def test_missing_property_is_not_deleted(self):
        self.upload(workbook(['property_id', 'address'], [[1001, 'Pune'], [1002, 'Nashik']]))
        self.upload(workbook(['property_id', 'address'], [[1001, 'Pune City']]))
        self.assertTrue(Property.objects.filter(property_id='1002').exists())

    def test_dry_run_does_not_save(self):
        response = self.upload(
            workbook(['property_id', 'market_rate'], [[1001, 2500]]),
            dry_run=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['dry_run'])
        self.assertEqual(response.data['inserted'], 1)
        self.assertFalse(Property.objects.filter(property_id='1001').exists())

"""Which property columns an XLSX file is allowed to write.

A column is updated only when that header is present in the uploaded file.
Columns that are absent from the file are never included in the UPDATE, so
they cannot be cleared to NULL.

current_market_rate, owner_name, status, created_at, and updated_at stay
protected unless the XLSX itself contains that column.
"""

PROPERTY_ID = 'property_id'

# Columns the import may write when the matching header is in the workbook.
XLSX_WRITABLE_FIELDS = (
    'address',
    'latitude',
    'longitude',
    'area_sqft',
    'market_rate',
    'current_market_rate',
    'owner_name',
    'status',
    'created_at',
    'updated_at',
)

# Left unchanged unless that exact column is in this XLSX.
PROTECTED_UNLESS_IN_FILE = (
    'current_market_rate',
    'owner_name',
    'status',
    'created_at',
    'updated_at',
)

NUMERIC_FIELDS = ('latitude', 'longitude', 'area_sqft', 'market_rate', 'current_market_rate')
DECIMAL_FIELDS = ('area_sqft', 'market_rate', 'current_market_rate')
TEXT_FIELDS = ('address', 'owner_name', 'status')
DATETIME_FIELDS = ('created_at', 'updated_at')

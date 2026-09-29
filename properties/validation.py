from datetime import datetime
from decimal import Decimal, InvalidOperation

from properties.columns import (
    DATETIME_FIELDS,
    DECIMAL_FIELDS,
    NUMERIC_FIELDS,
    PROPERTY_ID,
    TEXT_FIELDS,
)


class RowFailure(Exception):
    def __init__(self, message):
        self.message = message


def _is_blank(value):
    return value is None or (isinstance(value, str) and value.strip() == '')


def _decimal(value, field):
    try:
        number = Decimal(str(value).strip()) if not isinstance(value, Decimal) else value
    except (InvalidOperation, ValueError, TypeError):
        raise RowFailure(f'{field} must be a number.')
    return number


def _property_id(value):
    if _is_blank(value):
        raise RowFailure('property_id is required.')
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, Decimal) and value == value.to_integral():
        return str(int(value))
    text = str(value).strip()
    if text.endswith('.0') and text[:-2].isdigit():
        text = text[:-2]
    if not text:
        raise RowFailure('property_id is required.')
    return text[:64]


def _datetime(value, field):
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for pattern in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(text, pattern)
        except ValueError:
            continue
    raise RowFailure(f'{field} must be a date or date-time.')


def validate_row(values, columns_in_file):
    """Return a dict of fields this row may write. Blank cells are omitted."""
    prepared = {PROPERTY_ID: _property_id(values.get(PROPERTY_ID))}
    for field in columns_in_file:
        if field == PROPERTY_ID or field not in values:
            continue
        raw = values.get(field)
        if _is_blank(raw):
            continue
        if field in ('latitude', 'longitude'):
            number = _decimal(raw, field)
            limit = Decimal('90') if field == 'latitude' else Decimal('180')
            if not -limit <= number <= limit:
                raise RowFailure(f'{field} is out of range.')
            prepared[field] = number
        elif field in DECIMAL_FIELDS or field in NUMERIC_FIELDS:
            prepared[field] = _decimal(raw, field)
        elif field in DATETIME_FIELDS:
            prepared[field] = _datetime(raw, field)
        elif field in TEXT_FIELDS:
            prepared[field] = str(raw).strip()
    return prepared

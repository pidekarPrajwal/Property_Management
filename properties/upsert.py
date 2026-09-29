import logging
from datetime import datetime, timezone

from django.db import transaction

from properties.columns import PROPERTY_ID, PROTECTED_UNLESS_IN_FILE, XLSX_WRITABLE_FIELDS
from properties.models import Property, PropertySyncLog
from properties.validation import RowFailure, validate_row

logger = logging.getLogger('properties.sync')


def synchronize(parsed, filename, dry_run):
    """Insert or update properties. Importing this module does not write anything."""
    columns_in_file = [
        column for column in parsed['recognized_columns'] if column in XLSX_WRITABLE_FIELDS
    ]
    untouched = [column for column in PROTECTED_UNLESS_IN_FILE if column not in columns_in_file]
    inserted = updated = skipped = failed = 0
    errors = []
    ready = []
    seen = set()

    for row in parsed['rows']:
        if row['empty']:
            skipped += 1
            continue
        try:
            prepared = validate_row(row['values'], columns_in_file)
        except RowFailure as exc:
            failed += 1
            errors.append({'row': row['excel_row'], 'error': exc.message})
            continue
        property_id = prepared[PROPERTY_ID]
        if property_id in seen:
            skipped += 1
            errors.append({'row': row['excel_row'], 'property_id': property_id, 'error': 'Duplicate property_id in this file. The first row is kept.'})
            continue
        seen.add(property_id)
        ready.append(prepared)

    existing_ids = set(
        Property.objects.filter(property_id__in=[row[PROPERTY_ID] for row in ready]).values_list(
            'property_id', flat=True
        )
    )
    synced_at = datetime.now(timezone.utc).isoformat()

    def apply():
        nonlocal inserted, updated
        for prepared in ready:
            property_id = prepared[PROPERTY_ID]
            fields = {key: value for key, value in prepared.items() if key != PROPERTY_ID}
            if property_id in existing_ids:
                if fields:
                    Property.objects.filter(property_id=property_id).update(**fields)
                updated += 1
            else:
                Property.objects.create(property_id=property_id, **fields)
                inserted += 1

    if dry_run:
        inserted = sum(1 for row in ready if row[PROPERTY_ID] not in existing_ids)
        updated = sum(1 for row in ready if row[PROPERTY_ID] in existing_ids)
        message = 'Dry run only. No database changes were saved.'
    else:
        try:
            with transaction.atomic():
                apply()
                PropertySyncLog.objects.create(
                    filename=filename or 'upload.xlsx',
                    inserted=inserted,
                    updated=updated,
                    skipped=skipped,
                    failed=failed,
                )
        except Exception:
            logger.exception('XLSX synchronization rolled back file=%s', filename)
            raise
        message = 'XLSX synchronization completed'

    logger.info(
        'XLSX sync file=%s at=%s dry_run=%s inserted=%s updated=%s skipped=%s failed=%s',
        filename,
        synced_at,
        dry_run,
        inserted,
        updated,
        skipped,
        failed,
    )
    return {
        'success': True,
        'message': message,
        'filename': filename,
        'synced_at': synced_at,
        'dry_run': dry_run,
        'inserted': inserted,
        'updated': updated,
        'skipped': skipped,
        'failed': failed,
        'xlsx_columns': columns_in_file,
        'untouched_columns': untouched,
        'ignored_columns': parsed['ignored_columns'],
        'errors': errors[:50],
    }

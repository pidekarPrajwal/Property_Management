from django.db import migrations, models


def split_coordinates(apps, schema_editor):
    Site = apps.get_model('setup', 'Site')
    for site in Site.objects.all():
        points = site.coordinates or []
        site.latitude = [
            point.get('latitude') for point in points if isinstance(point, dict)
        ]
        site.longitude = [
            point.get('longitude') for point in points if isinstance(point, dict)
        ]
        site.save(update_fields=['latitude', 'longitude'])


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0005_site_coordinates'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='latitude',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(split_coordinates, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='site',
            name='coordinates',
        ),
    ]

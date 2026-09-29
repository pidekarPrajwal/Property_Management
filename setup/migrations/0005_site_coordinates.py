from django.db import migrations, models


def copy_points_to_polygon(apps, schema_editor):
    Site = apps.get_model('setup', 'Site')
    for site in Site.objects.all():
        if site.latitude is None or site.longitude is None:
            site.coordinates = []
        else:
            latitude = float(site.latitude)
            longitude = float(site.longitude)
            span = 0.004
            site.coordinates = [
                {'latitude': round(latitude - span, 6), 'longitude': round(longitude - span, 6)},
                {'latitude': round(latitude - span, 6), 'longitude': round(longitude + span, 6)},
                {'latitude': round(latitude + span, 6), 'longitude': round(longitude + span, 6)},
                {'latitude': round(latitude + span, 6), 'longitude': round(longitude - span, 6)},
            ]
        site.save(update_fields=['coordinates'])


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0004_project_map_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='coordinates',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(copy_points_to_polygon, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='site',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='site',
            name='longitude',
        ),
    ]

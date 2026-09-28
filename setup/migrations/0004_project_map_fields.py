from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0003_site_latitude_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='building_type',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='project',
            name='contractor',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='project',
            name='expected_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='latest_progress',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='phase',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
        migrations.AddField(
            model_name='project',
            name='work_order_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

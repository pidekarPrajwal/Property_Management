from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0006_site_latitude_longitude_lists'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='current_market_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
    ]

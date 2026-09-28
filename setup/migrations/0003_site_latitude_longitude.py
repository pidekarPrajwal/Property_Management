from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='site',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
    ]

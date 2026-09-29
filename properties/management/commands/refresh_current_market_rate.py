from django.core.management.base import BaseCommand

from properties.site_market_rate import map_site_market_rates, write_report


class Command(BaseCommand):
    help = 'Refresh each Site current_market_rate from the latest nearest Property market rate.'

    def add_arguments(self, parser):
        parser.add_argument('--radius-km', dest='radius_km', default=None)

    def handle(self, *args, **options):
        summary = map_site_market_rates(options['radius_km'])
        write_report(self.stdout, 'Refreshing current market rates...', summary)

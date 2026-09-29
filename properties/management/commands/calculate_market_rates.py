from django.core.management.base import BaseCommand

from properties.market_rate import calculate_current_market_rates


class Command(BaseCommand):
    help = 'Set current_market_rate from nearby property market rates. Does not run on import.'

    def add_arguments(self, parser):
        parser.add_argument('--radius-km', dest='radius_km', default=None)

    def handle(self, *args, **options):
        result = calculate_current_market_rates(options['radius_km'])
        self.stdout.write(self.style.SUCCESS(
            f"Updated current_market_rate on {result['updated']} properties within {result['radius_km']} km."
        ))

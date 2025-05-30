import csv
from django.core.management.base import BaseCommand
from product.models import HarmfulIngredient  # Update with the correct app name

class Command(BaseCommand):
    help = 'Import harmful ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('ChemicalName')  # Ensure this matches your CSV header
                if name:
                    HarmfulIngredient.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Successfully imported harmful ingredients'))

import csv
import os
from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv'

    def handle(self, *args, **options):
        file_path = os.path.join(BASE_DIR, 'data')
        with open(f'{file_path}/ingredients.csv',
                  'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            for line in reader:
                name, unit = line
                Ingredient.objects.get_or_create(name=name,
                                                 measurement_unit=unit)

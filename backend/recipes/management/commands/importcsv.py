import csv
import os
from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv'

    def handle(self, *args, **options):
        temp_data = []
        file_path = os.path.join(BASE_DIR, 'data')
        object_id = (Ingredient.objects.latest('id').id + 1
                     if Ingredient.objects.all().exists()
                     else 0)
        with open(f'{file_path}/ingredients.csv',
                  'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            for line in reader:
                name, unit = line
                if line[1] == '':
                    continue
                temp_data.append(Ingredient(id=object_id,
                                            name=name,
                                            measurement_unit=unit))
                object_id += 1
        Ingredient.objects.bulk_create(temp_data, batch_size=500)

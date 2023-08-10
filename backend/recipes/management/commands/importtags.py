from django.core.management.base import BaseCommand
from rest_framework.generics import CreateAPIView
from recipes.models import Tag


class Command(BaseCommand, CreateAPIView):
    def handle(self, *args, **options):
        Tag.objects.create(name='Ужин', color='blue', slug='dinner')
        Tag.objects.create(name='Завтрак', color='red', slug='breakfast')
        Tag.objects.create(name='обед', color='green', slug='lunch')

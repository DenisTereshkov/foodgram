import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт продуктов из data/ingredients.json'

    def handle(self, *args, **kwargs):
        with open('./data/ingredients.json', encoding='utf-8') as json_data:
            data = json.load(json_data)
        Ingredient.objects.bulk_create((
            Ingredient(**item) for item in data),
        )
        self.stdout.write(self.style.SUCCESS('Ингредиенты созданы спешно!'))
        with open('./data/tags.json', encoding='utf-8') as json_data:
            data = json.load(json_data)
        Tag.objects.bulk_create((
            Tag(**item) for item in data),
        )
        self.stdout.write(self.style.SUCCESS('Тэги созданы успешно!'))

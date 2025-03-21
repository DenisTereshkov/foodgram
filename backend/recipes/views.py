from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from .models import Recipe


def redirect_to_recipe(request, recipe_id):
    """Перенаправляет на страницу рецепта, если он существует."""
    if Recipe.objects.filter(id=recipe_id).exists():
        return redirect(f'/recipes/{recipe_id}/')
    else:
        raise ValidationError(f'Рецепт с id {recipe_id} отсутствует.')

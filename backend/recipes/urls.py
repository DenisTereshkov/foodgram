from django.urls import path

from recipes.views import redirect_to_recipe

app_name = 'recipes'

urlpatterns = [
    path('<int:recipe_id>', redirect_to_recipe, name='short_link'),
]

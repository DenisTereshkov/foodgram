from django.contrib import admin

from .models import Amount, Ingredient, Recipe, Tag


class AmountAdmin(admin.ModelAdmin):
    """Администратор для модели Amount."""
    model = Amount
    fields = ('recipe', 'ingredient', 'amount')


class IngredientAdmin(admin.ModelAdmin):
    """Администратор для модели Ingredient."""
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


class RecipeInline(admin.StackedInline):
    """Встраиваемый интерфейс для Amount в Recipe."""
    model = Amount
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    """Администратор для модели Recipe."""
    inlines = (
        RecipeInline,
    )
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    @admin.display(description='Количество добавлений в избранное')
    def favorites_count(self, obj):
        """Возвращает количество избранных рецептов."""
        return obj.favorite.count()


class TagAdmin(admin.ModelAdmin):
    """Администратор для модели Tag."""
    list_display = (
        'name',
        'slug'
    )
    search_fields = ('name',)


admin.site.empty_value_display = '(None)'
admin.site.register(Amount, AmountAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)

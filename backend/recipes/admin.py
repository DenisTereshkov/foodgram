from django.contrib import admin

from .models import Amount, Ingredient, Recipe, Tag


class AmountAdmin(admin.ModelAdmin):
    ...


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


class RecipeInline(admin.StackedInline):
    model = Amount
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = (
        RecipeInline,
    )
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def favorites_count(self, obj):
        """Возвращает количество избранных."""
        return obj.favorite.count()


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    search_fields = ('name',)


admin.site.empty_value_display = '(None)'
admin.site.register(Amount)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)

from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models, IntegrityError

from backend.constant import (
    FIELD_NAME_LENGTH,
    MIN_AMOUNT,
    MAX_AMOUNT,
    MIN_COOKING_TIME,
    TEXT_LENGTH
)

User = get_user_model()


class NameModel(models.Model):
    """Базовая модель с именем объекта."""
    name = models.CharField(
        max_length=FIELD_NAME_LENGTH,
        verbose_name='Название'
    )

    class Meta:
        abstract = True
        ordering = ('name')

    def __str__(self):
        return self.name


class Tag(NameModel):
    """Модель тэгов."""
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(NameModel):
    """Модель ингредиентов."""
    measurement_unit = models.CharField(
        max_length=FIELD_NAME_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(NameModel):
    """Модель рецептов."""
    tags = models.ManyToManyField(
        Tag,
        blank=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Amount',
        blank=False,
        verbose_name='Ингредиент',
    )
    image = models.ImageField(
        upload_to='recipes',
        blank=True,
        null=True,
        default=None,
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        max_length=TEXT_LENGTH,
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Amount(models.Model):
    """Вспомогательный класс для связи рецепта и количества ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        )
    )

    class Meta:
        verbose_name = 'Ингредиент и его количество в рецепте'
        verbose_name_plural = 'Ингредиенты и их количество в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount}'
                f'{self.ingredient.measurement_unit} '
                f'Рецепт: {self.recipe.name}')

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise AssertionError(
                "Комбинация рецепта и ингредиента уже существует."
            )


class FavoriteShoppingCartBaseModel(models.Model):
    """Базовый класс для избранного и корзины пользователя."""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class FavoriteRecipe(FavoriteShoppingCartBaseModel):
    """Вспомогательный класс для избранных рецептов пользователя."""

    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        default_related_name = 'favorite'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorire_recipe_user'
            ),
        )

    def __str__(self):
        return self.recipe.name


class ShoppingCart(FavoriteShoppingCartBaseModel):
    """Вспомогательный класс для рецептов в корзине пользователя."""

    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'корзины покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_cart_recipe_user'
            ),
        )

    def __str__(self):
        return self.recipe.name

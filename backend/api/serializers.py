import base64
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from backend.constant import MAX_AMOUNT, MIN_COOKING_TIME, MIN_AMOUNT
from recipes.models import (
    Amount,
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для изображений."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователей."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.is_following.filter(
            is_following=obj
        ).exists()


class FollowSerializer(UserSerializer):
    """Сериализатор для модели подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', None)
        recipes = Recipe.objects.filter(author=obj)
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class FollowCreateDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""
    class Meta:
        model = Follow
        fields = 'user', 'is_following'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'is_following'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['is_following']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return FollowSerializer(
            instance.is_following,
            context={'request': request}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тэгов."""
    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag
        read_only_fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class AmountSerializer(serializers.ModelSerializer):
    """Сериализатор для модели количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id', read_only=True)
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )
        model = Amount


class AmountCreateSerializer(serializers.ModelSerializer):
    """Проверка ингредиента при создании рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                MIN_AMOUNT,
                f'Количество ингредиента должно быть больше {MIN_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                f'Количество ингредиента должно быть больше {MAX_AMOUNT}'
            )
        )
    )

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах в рецепте."""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                MIN_AMOUNT,
                f'Количество ингредиента должно быть больше {MIN_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                f'Количество ингредиента должно быть больше {MAX_AMOUNT}'
            )
        )
    )

    class Meta:
        model = Amount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецептов."""
    tags = TagSerializer(many=True)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='amount')
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and user.favorite.filter(
            recipe=obj
        ).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated and user.shopping_cart.filter(
            recipe=obj
        ).exists())

    def get_context(self):
        return self.context.get('request')


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""
    class Meta():
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientCreateSerializer(
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                f'Время приготовления меньше {MIN_COOKING_TIME} мин.'
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate_items(self, items, item_model, item_name):
        if not items:
            raise serializers.ValidationError(
                {item_name: f'Поле {item_name} не может быть пустым'})
        if len(items) != len(set(items)):
            raise serializers.ValidationError(
                {item_name: f'Объекты в {item_name} не должны повторяться'})
        for item in items:
            if not item_model.objects.filter(id=item).exists():
                raise serializers.ValidationError(
                    {item_name: f'Объект с id {item} не существует'})

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Поле ingredients не может быть пустым.'}
            )
        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        tags = data.get('tags')
        self.validate_items(
            items=ingredients_id,
            item_model=Ingredient,
            item_name='ingredients'
        )
        self.validate_items(items=tags, item_model=Tag, item_name='tags')
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def create_ingredients(self, ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            ingredients_list.append(
                Amount(
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                    ingredient=get_object_or_404(
                        Ingredient,
                        id=ingredient.get('id')
                    ),
                )
            )
        Amount.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        validated_data.update({'author': self.context.get('request').user})
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients=ingredients, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.save()
        instance.ingredients.clear()
        self.create_ingredients(ingredients=ingredients, recipe=instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data

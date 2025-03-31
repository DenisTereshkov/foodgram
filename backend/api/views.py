from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Amount,
    Ingredient,
    FavoriteRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from .permissions import AuthorOrReadOnly
from .paginators import LimitPaginator
from .serializers import (
    AvatarSerializer,
    CreateRecipeSerializer,
    IngredientSerializer,
    FavoriteRecipeSerializer,
    FollowCreateDeleteSerializer,
    FollowSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer
)
from users.models import Follow

User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPaginator
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AuthorOrReadOnly
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        if self.action in ('favorite', 'shopping_cart'):
            return ShortRecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def create_delete_favorite_or_cart(
        request,
        pk,
        serializer,
        model,
        response_text
    ):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        serializer = serializer(
            data={
                'user': user.id,
                'recipe': recipe.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        model.objects.get(recipe=recipe).delete()
        return Response(
            response_text,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.create_delete_favorite_or_cart(
            request=request,
            pk=pk,
            serializer=FavoriteRecipeSerializer,
            model=FavoriteRecipe,
            response_text='Рецепт удалён из избранного.'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.create_delete_favorite_or_cart(
            request=request,
            pk=pk,
            serializer=ShoppingCartSerializer,
            model=ShoppingCart,
            response_text='Рецепт удалён из корзины.',
        )

    @action(
        methods=['get'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_list = []
        shopping_cart_ingredients = (
            Amount.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        )
        for ingredient in shopping_cart_ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            total_amount = ingredient['total_amount']
            shopping_list.append(
                f"{name} ({measurement_unit}) — {total_amount}"
            )
        shopping_list_text = "\n".join(shopping_list)
        return FileResponse(
            shopping_list_text,
            content_type="text/plain",
            filename=f'{request.user.username}_shopping_cart.txt',
        )

    @action(detail=True, url_path="get-link")
    def get_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = get_object_or_404(Recipe, id=pk)
        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("recipes:short_link", args=[recipe.id])
                )
            },
            status=status.HTTP_200_OK,
        )


class FoodgramUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""
    pagination_class = LimitPaginator
    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['me', 'set_password']:
            return [IsAuthenticated(), ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.request.method == 'GET':
            return UserSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated, ]
    )
    def user_avatar(self, request):
        user = self.request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<id>\d+)/subscribe',
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, id):
        user = self.request.user
        following = get_object_or_404(User, pk=id)
        has_following = Follow.objects.filter(
            is_following=following,
            user=user
        )
        serializer = FollowCreateDeleteSerializer(
            data={'user': user.id, 'is_following': following.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        has_following.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="subscriptions",
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            is_following__user=self.request.user
        )
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            subscriptions, many=True, context={"request": request}
        )
        return Response(serializer.data)

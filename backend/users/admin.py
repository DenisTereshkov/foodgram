from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow
User = get_user_model()


class UserInline(admin.StackedInline):
    """
    Встраиваемый интерфейс администратора для модели Follow.
    Позволяет редактировать экземпляры Follow в админ-зоне пользователя.
    """
    model = Follow
    fk_name = 'is_following'
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Администратор пользователей.
    Настраивает отображение списка пользователей и управления подписками.
    """
    inlines = (UserInline, )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'followers_count',
        'recipes_count',
    )
    search_fields = ('email', 'first_name', )

    @admin.display(description='Подписчики')
    def followers_count(self, obj):
        """
        Количество подписчиков у пользователя.

        :param obj: Экземпляр пользователя.
        :return: Количество подписчиков.
        """
        return obj.is_following.count()

    @admin.display(description='Всего рецептов')
    def recipes_count(self, obj):
        """
        Общее количество рецептов, созданных пользователем.

        :param obj: Экземпляр пользователя.
        :return: Количество рецептов.
        """
        return obj.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Администратор для модели Follow.
    Настраивает отображение списка подписок.
    """
    list_display = ('user', 'is_following')


admin.site.empty_value_display = '(None)'

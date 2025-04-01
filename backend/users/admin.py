from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Follow
User = get_user_model()


class UserInline(admin.StackedInline):
    model = Follow
    fk_name = 'is_following'
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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
        return obj.is_following.count()

    @admin.display(description='Всего рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_following')


admin.site.empty_value_display = '(None)'

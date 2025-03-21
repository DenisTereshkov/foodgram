from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow
User = get_user_model()


class UserInline(admin.StackedInline):
    model = Follow
    fk_name = 'is_following'
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = (UserInline, )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'first_name', )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_following')


admin.site.empty_value_display = '(None)'
admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)

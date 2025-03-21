from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Пермишен для проверки на автора."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )

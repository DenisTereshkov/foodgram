from rest_framework.pagination import PageNumberPagination

from backend.constant import PAGE_SIZE


class LimitPaginator(PageNumberPagination):
    """Пагинатор с атрибутом количества объектов на странице."""
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE

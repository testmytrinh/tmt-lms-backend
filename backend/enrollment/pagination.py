from rest_framework import pagination


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200

from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 1000
    max_limit = 1000000
    min_limit = 1
    min_offset = 0
    max_offset = 1000000
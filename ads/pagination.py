from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .models import Ad

class LimitOffsetWithCategoryPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data,
            'lca_category': None if not data else data[0].get('lca_category')
        })

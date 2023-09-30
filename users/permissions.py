from rest_framework import permissions

from .models import ShilengaeUser

class AdminPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.type == ShilengaeUser.ROLE.ADMIN and super().has_permission(request, view)

class SuperAdminPermissions(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.type == ShilengaeUser.ROLE.SUPERADMIN and super().has_permission(request, view)


class AdUpdatePermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
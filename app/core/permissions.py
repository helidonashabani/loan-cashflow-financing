from rest_framework.permissions import BasePermission


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return False


class IsInvestor(BasePermission):
    def has_permission(self, request, view):
        return False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

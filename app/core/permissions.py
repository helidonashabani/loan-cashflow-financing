from rest_framework.permissions import BasePermission


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_investor or request.user.is_superuser


class IsInvestor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_investor or request.user.is_superuser


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

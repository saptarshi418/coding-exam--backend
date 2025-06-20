# contests/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission

from rest_framework.permissions import SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True  # Allow GET, HEAD, OPTIONS for everyone
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'contest'):
            return obj.contest.created_by == request.user
        return False




class IsOrganization(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'organization'


# contests/permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj can be Contest or Question
        if hasattr(obj, 'created_by'):
            # Contest instance
            return obj.created_by == request.user
        elif hasattr(obj, 'contest'):
            # Question instance
            return obj.contest.created_by == request.user
        return False

    



class IsOrganization(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'organization'


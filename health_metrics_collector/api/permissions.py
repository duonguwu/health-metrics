from rest_framework.permissions import BasePermission

class IsOwnerPermission(BasePermission):
    """
    Permission class to check if the requesting user is the owner of the object.

    Methods:
        has_object_permission(request, view, obj):
            Checks if the user associated with the object is the same as the requesting user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id 

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSeller(BasePermission):
    message = "You must become a seller to perform this action."

    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        if not request.user.is_authenticated:
            return False
        
        try:
            return request.user.profile.is_seller
        except:
            return False


class IsProductOwnerOrReadOnly(BasePermission):
    message = "You can only edit your own products."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and obj.posted_by == request.user


class IsCommentOwnerOrReadOnly(BasePermission):
    message = "You can edit only your own comments."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and obj.user == request.user


class IsProductImageOwnerOrReadOnly(BasePermission):
    message = "You can modify only your own product images."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and obj.product.posted_by == request.user

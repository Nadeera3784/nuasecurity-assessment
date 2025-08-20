from rest_framework.permissions import BasePermission
from .models import Admin, Supplier


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, "neo4j_user"):
            return False
        return isinstance(request.neo4j_user, Admin)


class IsSupplier(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, "neo4j_user"):
            return False
        return isinstance(request.neo4j_user, Supplier)


class IsAdminOrSupplier(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, "neo4j_user"):
            return False
        neo4j_user = request.neo4j_user
        return isinstance(neo4j_user, (Admin, Supplier))


class IsSupplierOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, "neo4j_user"):
            return False
        return isinstance(request.neo4j_user, (Admin, Supplier))

    def has_object_permission(self, request, view, obj):
        neo4j_user = request.neo4j_user

        if isinstance(neo4j_user, Admin):
            return True

        if isinstance(neo4j_user, Supplier):
            try:
                supplier_grocery = neo4j_user.responsible_for.single()
                if not supplier_grocery:
                    return False

                if hasattr(obj, "belongs_to_grocery"):
                    item_grocery = obj.belongs_to_grocery.single()
                    return item_grocery and item_grocery.uid == supplier_grocery.uid
                elif hasattr(obj, "grocery"):
                    income_grocery = obj.grocery.single()
                    return income_grocery and income_grocery.uid == supplier_grocery.uid
                elif hasattr(obj, "uid"):
                    return obj.uid == supplier_grocery.uid

            except Exception:
                return False

        return False


class CanReadItems(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request, "neo4j_user"):
            return False
        return isinstance(request.neo4j_user, (Admin, Supplier))

    def has_object_permission(self, request, view, obj):
        neo4j_user = request.neo4j_user

        if isinstance(neo4j_user, Admin):
            return True

        if isinstance(neo4j_user, Supplier):
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return True

            try:
                supplier_grocery = neo4j_user.responsible_for.single()
                if not supplier_grocery:
                    return False

                if hasattr(obj, "belongs_to_grocery"):
                    item_grocery = obj.belongs_to_grocery.single()
                    return item_grocery and item_grocery.uid == supplier_grocery.uid

            except Exception:
                return False

        return False

from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path

from .models import Admin as Neo4jAdmin, Supplier, Grocery, Item, DailyIncome


class Neo4jModelAdmin:
    def __init__(self, model, admin_site):
        self.model = model
        self.admin_site = admin_site

    def get_urls(self):
        urls = [
            path(
                "",
                self.changelist_view,
                name=f"{self.model.__name__.lower()}_changelist",
            ),
            path(
                "<str:object_id>/",
                self.change_view,
                name=f"{self.model.__name__.lower()}_change",
            ),
        ]
        return urls

    def changelist_view(self, request):
        if not (
            request.user.is_active
            and (request.user.is_staff or request.user.is_superuser)
        ):
            from django.contrib import messages

            messages.error(request, "You don't have permission to view this page.")
            return redirect("/admin/")

        try:
            objects = list(self.model.nodes.all())

            print(f"Found {len(objects)} {self.model.__name__} objects")
            for obj in objects[:3]:
                print(f"  - {obj}")

            context = {
                "title": f"{self.model.__name__} List",
                "objects": objects,
                "model_name": self.model.__name__,
                "opts": {"verbose_name_plural": f"{self.model.__name__}s"},
                "object_count": len(objects),
            }
            return render(request, "admin/neo4j_changelist.html", context)
        except Exception as e:
            print(f"Error in changelist_view for {self.model.__name__}: {e}")
            context = {
                "title": f"{self.model.__name__} List",
                "error": str(e),
                "model_name": self.model.__name__,
                "opts": {"verbose_name_plural": f"{self.model.__name__}s"},
                "object_count": 0,
            }
            return render(request, "admin/neo4j_changelist.html", context)

    def change_view(self, request, object_id):
        if not (
            request.user.is_active
            and (request.user.is_staff or request.user.is_superuser)
        ):
            from django.contrib import messages

            messages.error(request, "You don't have permission to view this page.")
            return redirect("/admin/")

        try:
            obj = self.model.nodes.get(uid=object_id)

            obj_dict = {}

            properties_to_show = [
                "uid",
                "name",
                "email",
                "user_type",
                "location",
                "item_type",
                "item_location",
                "price",
                "amount",
                "date",
                "is_active",
                "is_deleted",
                "created_at",
                "updated_at",
            ]

            for prop in properties_to_show:
                try:
                    if hasattr(obj, prop):
                        value = getattr(obj, prop)
                        if value is not None:
                            formatted_key = prop.replace("_", " ").title()
                            obj_dict[formatted_key] = str(value)
                except Exception as e:
                    print(f"Error getting property {prop}: {e}")
                    continue

            try:
                if hasattr(obj, "belongs_to_grocery"):
                    grocery = obj.belongs_to_grocery.single()
                    if grocery:
                        obj_dict["Grocery"] = grocery.name

                if hasattr(obj, "added_by"):
                    supplier = obj.added_by.single()
                    if supplier:
                        obj_dict["Added By Supplier"] = supplier.name

                if hasattr(obj, "recorded_by"):
                    supplier = obj.recorded_by.single()
                    if supplier:
                        obj_dict["Recorded By Supplier"] = supplier.name
            except Exception as e:
                print(f"Error getting relationships: {e}")

            context = {
                "title": f"{self.model.__name__}: {object_id[:8]}...",
                "object": obj,
                "object_dict": obj_dict,
                "model_name": self.model.__name__,
                "opts": {"verbose_name": self.model.__name__},
                "object_id": object_id,
            }
            return render(request, "admin/neo4j_change.html", context)
        except Exception as e:
            print(f"Error in change_view: {e}")
            context = {
                "title": f"{self.model.__name__}: Not Found",
                "error": f"{self.model.__name__} with ID {object_id} not found. Error: {str(e)}",
                "model_name": self.model.__name__,
                "opts": {"verbose_name": self.model.__name__},
            }
            return render(request, "admin/neo4j_change.html", context)


class CustomAdminSite(admin.AdminSite):
    site_header = "Grocery Management System Admin"
    site_title = "Grocery Admin"
    index_title = "Welcome to Grocery Management System Administration"

    def has_permission(self, request):
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "neo4j-stats/",
                self.admin_view(self.neo4j_stats_view),
                name="neo4j_stats",
            ),
            path(
                "admins/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).changelist_view),
                name="neo4j_admin_changelist",
            ),
            path(
                "admins/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).change_view),
                name="neo4j_admin_change",
            ),
            path(
                "suppliers/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).changelist_view),
                name="neo4j_supplier_changelist",
            ),
            path(
                "suppliers/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).change_view),
                name="neo4j_supplier_change",
            ),
            path(
                "groceries/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).changelist_view),
                name="neo4j_grocery_changelist",
            ),
            path(
                "groceries/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).change_view),
                name="neo4j_grocery_change",
            ),
            path(
                "items/",
                self.admin_view(Neo4jModelAdmin(Item, self).changelist_view),
                name="neo4j_item_changelist",
            ),
            path(
                "items/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Item, self).change_view),
                name="neo4j_item_change",
            ),
            path(
                "daily-income/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).changelist_view),
                name="neo4j_dailyincome_changelist",
            ),
            path(
                "daily-income/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).change_view),
                name="neo4j_dailyincome_change",
            ),
        ]
        return custom_urls + urls

    def neo4j_stats_view(self, request):
        try:
            admin_count = len(Neo4jAdmin.nodes.all())
            supplier_count = len(Supplier.nodes.all())
            grocery_count = len(Grocery.nodes.all())
            item_count = len(Item.nodes.all())
            income_count = len(DailyIncome.nodes.all())

            stats = {
                "Admins": admin_count,
                "Suppliers": supplier_count,
                "Groceries": grocery_count,
                "Items": item_count,
                "Daily Income Records": income_count,
            }

            # Print debug info
            print(f"Neo4j Stats: {stats}")

            context = {
                "title": "Neo4j Database Statistics",
                "stats": stats,
                "total_nodes": sum(stats.values()),
            }
            return render(request, "admin/neo4j_stats.html", context)
        except Exception as e:
            print(f"Error in neo4j_stats_view: {e}")
            context = {
                "title": "Neo4j Database Statistics",
                "error": str(e),
            }
            return render(request, "admin/neo4j_stats.html", context)

    def index(self, request, extra_context=None):
        if not self.has_permission(request):
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())

        extra_context = extra_context or {}
        extra_context["neo4j_models"] = [
            {"name": "Admins", "url": "admin:neo4j_admin_changelist"},
            {"name": "Suppliers", "url": "admin:neo4j_supplier_changelist"},
            {"name": "Groceries", "url": "admin:neo4j_grocery_changelist"},
            {"name": "Items", "url": "admin:neo4j_item_changelist"},
            {"name": "Daily Income", "url": "admin:neo4j_dailyincome_changelist"},
            {"name": "Database Stats", "url": "admin:neo4j_stats"},
        ]
        return super().index(request, extra_context)


admin_site = CustomAdminSite(name="grocery_admin")


class DummyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )


from django.contrib.auth.models import User, Group

admin_site.register(User, DummyAdmin)
admin_site.register(Group, DummyAdmin)

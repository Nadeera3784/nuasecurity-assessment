from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.contrib import messages

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
                "add/",
                self.add_view,
                name=f"{self.model.__name__.lower()}_add",
            ),
            path(
                "<str:object_id>/",
                self.change_view,
                name=f"{self.model.__name__.lower()}_change",
            ),
            path(
                "<str:object_id>/edit/",
                self.edit_view,
                name=f"{self.model.__name__.lower()}_edit",
            ),
            path(
                "<str:object_id>/delete/",
                self.delete_view,
                name=f"{self.model.__name__.lower()}_delete",
            ),
        ]
        return urls

    def get_form_class(self):
        class GroceryForm(forms.Form):
            name = forms.CharField(max_length=100)
            location = forms.CharField(max_length=200)
            is_active = forms.BooleanField(required=False, initial=True)

        class AdminForm(forms.Form):
            name = forms.CharField(max_length=100)
            email = forms.EmailField()
            password = forms.CharField(widget=forms.PasswordInput(), required=True)

        class SupplierForm(forms.Form):
            name = forms.CharField(max_length=100)
            email = forms.EmailField()
            password = forms.CharField(widget=forms.PasswordInput(), required=False)
            grocery_id = forms.CharField(required=False)

        class ItemForm(forms.Form):
            name = forms.CharField(max_length=100)
            item_type = forms.CharField(max_length=50)
            item_location = forms.CharField(max_length=100)
            price = forms.FloatField(min_value=0)
            grocery_id = forms.CharField(required=False)

        class DailyIncomeForm(forms.Form):
            date = forms.DateTimeField()
            amount = forms.FloatField(min_value=0)
            grocery_id = forms.CharField(required=False)

        if self.model.__name__ == "Grocery":
            return GroceryForm
        if self.model.__name__ == "Admin":
            return AdminForm
        if self.model.__name__ == "Supplier":
            return SupplierForm
        if self.model.__name__ == "Item":
            return ItemForm
        if self.model.__name__ == "DailyIncome":
            return DailyIncomeForm
        return forms.Form

    def changelist_view(self, request):
        def is_supplier(u):
            try:
                from django.contrib.auth.models import Group

                return (
                    u.is_active
                    and Group.objects.filter(user=u, name="Supplier").exists()
                )
            except Exception:
                return False

        def is_admin(u):
            try:
                from django.contrib.auth.models import Group

                in_supplier_group = Group.objects.filter(
                    user=u, name="Supplier"
                ).exists()
            except Exception:
                in_supplier_group = False
            return (
                u.is_active and (u.is_staff or u.is_superuser) and not in_supplier_group
            )

        model_name = self.model.__name__
        if not (
            is_admin(request.user)
            or (is_supplier(request.user) and model_name in ["Item", "DailyIncome"])
        ):
            messages.error(request, "You don't have permission to view this page.")
            return redirect("/admin/")

        try:
            objects = list(self.model.nodes.all())

            print(f"Found {len(objects)} {self.model.__name__} objects")
            for obj in objects[:3]:
                print(f"  - {obj}")

            if is_supplier(request.user) and model_name in ["Item", "DailyIncome"]:
                try:
                    login_email = getattr(request.user, "email", None) or getattr(
                        request.user, "username", None
                    )
                    supplier_node = Supplier.nodes.get(email=login_email)
                    supplier_grocery = supplier_node.responsible_for.single()
                    if supplier_grocery:
                        if model_name == "Item":
                            scoped = []
                            for it in objects:
                                try:
                                    g = it.belongs_to_grocery.single()
                                    if g and g.uid == supplier_grocery.uid:
                                        scoped.append(it)
                                except Exception:
                                    continue
                            objects = scoped
                        else:  # DailyIncome
                            scoped = []
                            for inc in objects:
                                try:
                                    g = inc.grocery.single()
                                    if g and g.uid == supplier_grocery.uid:
                                        scoped.append(inc)
                                except Exception:
                                    continue
                            objects = scoped
                except Exception:
                    objects = []

            context = {
                "title": f"{self.model.__name__} List",
                "objects": objects,
                "model_name": self.model.__name__,
                "opts": {"verbose_name_plural": f"{self.model.__name__}s"},
                "object_count": len(objects),
                "can_add": True,
            }

            if self.model.__name__ == "DailyIncome":
                from datetime import datetime

                daily_totals = {}
                grand_total = 0.0
                for inc in objects:
                    try:
                        day_key = str(inc.date.date()) if inc.date else None
                        if not day_key:
                            continue
                        daily_totals[day_key] = daily_totals.get(day_key, 0.0) + float(
                            inc.amount or 0.0
                        )
                        grand_total += float(inc.amount or 0.0)
                    except Exception:
                        continue

                today_key = str(datetime.utcnow().date())
                today_total = daily_totals.get(today_key, 0.0)

                sorted_totals = [
                    {"date": k, "total": v}
                    for k, v in sorted(
                        daily_totals.items(), key=lambda x: x[0], reverse=True
                    )
                ]

                context.update(
                    {
                        "daily_totals": sorted_totals,
                        "today_total": today_total,
                        "grand_total": grand_total,
                        "can_add": is_supplier(request.user),
                    }
                )
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
        def is_supplier(u):
            try:
                from django.contrib.auth.models import Group

                return (
                    u.is_active
                    and Group.objects.filter(user=u, name="Supplier").exists()
                )
            except Exception:
                return False

        def is_admin(u):
            try:
                from django.contrib.auth.models import Group

                in_supplier_group = Group.objects.filter(
                    user=u, name="Supplier"
                ).exists()
            except Exception:
                in_supplier_group = False
            return (
                u.is_active and (u.is_staff or u.is_superuser) and not in_supplier_group
            )

        model_name = self.model.__name__
        if not (
            is_admin(request.user)
            or (is_supplier(request.user) and model_name in ["Item", "DailyIncome"])
        ):
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
                "allow_delete": self.model.__name__
                in ["Item", "Grocery", "Admin", "Supplier"],
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

    def add_view(self, request):
        def is_supplier(u):
            try:
                from django.contrib.auth.models import Group

                return (
                    u.is_active
                    and Group.objects.filter(user=u, name="Supplier").exists()
                )
            except Exception:
                return False

        def is_admin(u):
            try:
                from django.contrib.auth.models import Group

                in_supplier_group = Group.objects.filter(
                    user=u, name="Supplier"
                ).exists()
            except Exception:
                in_supplier_group = False
            return (
                u.is_active and (u.is_staff or u.is_superuser) and not in_supplier_group
            )

        model_name = self.model.__name__
        if not (
            is_admin(request.user)
            or (is_supplier(request.user) and model_name in ["Item", "DailyIncome"])
        ):
            messages.error(request, "You don't have permission to add records.")
            return redirect("/admin/")

        FormClass = self.get_form_class()
        if request.method == "POST":
            form = FormClass(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                try:
                    if self.model.__name__ == "Grocery":
                        obj = Grocery(name=data["name"], location=data["location"])
                        obj.is_active = data.get("is_active", True)
                        obj.save()
                    elif self.model.__name__ == "Admin":
                        obj = Neo4jAdmin(name=data["name"], email=data["email"])
                        obj.set_password(data["password"])
                        obj.save()
                        try:
                            from django.contrib.auth.models import (
                                User as DjangoUser,
                                Group,
                            )

                            django_user, _created = DjangoUser.objects.get_or_create(
                                username=obj.email, defaults={"email": obj.email}
                            )
                            django_user.email = obj.email
                            django_user.first_name = obj.name
                            django_user.is_active = True
                            django_user.is_staff = True
                            django_user.is_superuser = True
                            django_user.set_password(data["password"])
                            django_user.save()

                            admin_group, _ = Group.objects.get_or_create(name="Admin")
                            django_user.groups.add(admin_group)
                        except Exception as e:
                            messages.warning(
                                request,
                                f"Admin created, but failed to sync Django user: {e}",
                            )
                    elif self.model.__name__ == "Supplier":
                        obj = Supplier(name=data["name"], email=data["email"])
                        raw_password = data.get("password") or "changeme123"
                        obj.set_password(raw_password)
                        obj.save()
                        try:
                            from django.contrib.auth.models import (
                                User as DjangoUser,
                                Group,
                            )

                            django_user, _created = DjangoUser.objects.get_or_create(
                                username=obj.email, defaults={"email": obj.email}
                            )
                            django_user.email = obj.email
                            django_user.first_name = obj.name
                            django_user.is_active = True
                            django_user.is_staff = False
                            django_user.is_superuser = False
                            django_user.set_password(raw_password)
                            django_user.save()

                            supplier_group, _ = Group.objects.get_or_create(
                                name="Supplier"
                            )
                            django_user.groups.add(supplier_group)
                        except Exception as e:
                            messages.warning(
                                request,
                                f"Supplier created, but failed to sync Django user: {e}",
                            )

                        grocery_id = data.get("grocery_id")
                        if grocery_id:
                            try:
                                grocery = Grocery.nodes.get(uid=grocery_id)
                                existing = obj.responsible_for.single()
                                if existing:
                                    obj.responsible_for.disconnect(existing)
                                obj.responsible_for.connect(grocery)
                            except Grocery.DoesNotExist:
                                pass
                    elif self.model.__name__ == "Item":
                        obj = Item(
                            name=data["name"],
                            item_type=data["item_type"],
                            item_location=data["item_location"],
                            price=data["price"],
                        )
                        obj.save()
                        try:
                            from django.contrib.auth.models import Group

                            is_sup = Group.objects.filter(
                                user=request.user, name="Supplier"
                            ).exists()
                        except Exception:
                            is_sup = False

                        if is_sup:
                            try:
                                login_email = getattr(
                                    request.user, "email", None
                                ) or getattr(request.user, "username", None)
                                supplier_node = Supplier.nodes.get(email=login_email)
                                supplier_grocery = (
                                    supplier_node.responsible_for.single()
                                )
                                if not supplier_grocery:
                                    messages.error(
                                        request, "No grocery assigned to supplier"
                                    )
                                    return redirect(request.path.replace("add/", ""))
                                supplier_grocery.items.connect(obj)
                            except Exception:
                                messages.error(
                                    request, "Could not assign item to supplier grocery"
                                )
                        else:
                            grocery_id = data.get("grocery_id")
                            if grocery_id:
                                try:
                                    grocery = Grocery.nodes.get(uid=grocery_id)
                                    grocery.items.connect(obj)
                                except Grocery.DoesNotExist:
                                    pass
                    elif self.model.__name__ == "DailyIncome":
                        obj = DailyIncome(date=data["date"], amount=data["amount"])
                        obj.save()
                        try:
                            from django.contrib.auth.models import Group

                            is_sup = Group.objects.filter(
                                user=request.user, name="Supplier"
                            ).exists()
                        except Exception:
                            is_sup = False

                        if is_sup:
                            try:
                                login_email = getattr(
                                    request.user, "email", None
                                ) or getattr(request.user, "username", None)
                                supplier_node = Supplier.nodes.get(email=login_email)
                                supplier_grocery = (
                                    supplier_node.responsible_for.single()
                                )
                                if not supplier_grocery:
                                    messages.error(
                                        request, "No grocery assigned to supplier"
                                    )
                                    return redirect(request.path.replace("add/", ""))
                                supplier_grocery.daily_incomes.connect(obj)
                            except Exception:
                                messages.error(
                                    request,
                                    "Could not assign income to supplier grocery",
                                )
                        else:
                            grocery_id = data.get("grocery_id")
                            if grocery_id:
                                try:
                                    grocery = Grocery.nodes.get(uid=grocery_id)
                                    grocery.daily_incomes.connect(obj)
                                except Grocery.DoesNotExist:
                                    pass
                    else:
                        messages.error(request, "Unsupported model")
                        return redirect("/admin/")

                    messages.success(
                        request, f"{self.model.__name__} created successfully"
                    )
                    return redirect(request.path.replace("add/", ""))
                except Exception as e:
                    messages.error(
                        request, f"Error creating {self.model.__name__}: {e}"
                    )
        else:
            form = FormClass()

        context = {
            "title": f"Add {self.model.__name__}",
            "form": form,
            "model_name": self.model.__name__,
        }
        return render(request, "admin/neo4j_form.html", context)

    def edit_view(self, request, object_id):
        def is_supplier(u):
            try:
                from django.contrib.auth.models import Group

                return (
                    u.is_active
                    and Group.objects.filter(user=u, name="Supplier").exists()
                )
            except Exception:
                return False

        def is_admin(u):
            try:
                from django.contrib.auth.models import Group

                in_supplier_group = Group.objects.filter(
                    user=u, name="Supplier"
                ).exists()
            except Exception:
                in_supplier_group = False
            return (
                u.is_active and (u.is_staff or u.is_superuser) and not in_supplier_group
            )

        model_name = self.model.__name__
        if not (
            is_admin(request.user)
            or (is_supplier(request.user) and model_name in ["Item", "DailyIncome"])
        ):
            messages.error(request, "You don't have permission to edit records.")
            return redirect("/admin/")

        FormClass = self.get_form_class()
        try:
            obj = self.model.nodes.get(uid=object_id)
        except Exception as e:
            messages.error(request, f"Record not found: {e}")
            return redirect("../")

        initial = {}
        for field in FormClass.base_fields.keys():
            if hasattr(obj, field):
                initial[field] = getattr(obj, field)

        if request.method == "POST":
            form = FormClass(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                try:
                    if self.model.__name__ == "Grocery":
                        obj.name = data.get("name", obj.name)
                        obj.location = data.get("location", obj.location)
                        obj.is_active = data.get("is_active", obj.is_active)
                        obj.save()
                    elif self.model.__name__ == "Admin":
                        old_email = obj.email
                        obj.name = data.get("name", obj.name)
                        obj.email = data.get("email", obj.email)
                        if data.get("password"):
                            obj.set_password(data["password"])
                        obj.save()
                        try:
                            from django.contrib.auth.models import (
                                User as DjangoUser,
                                Group,
                            )

                            django_user = (
                                DjangoUser.objects.filter(username=old_email).first()
                                or DjangoUser.objects.filter(username=obj.email).first()
                            )
                            if django_user is None:
                                django_user = DjangoUser(
                                    username=obj.email, email=obj.email
                                )
                            django_user.username = obj.email
                            django_user.email = obj.email
                            django_user.first_name = obj.name
                            django_user.is_active = True
                            django_user.is_staff = True
                            django_user.is_superuser = True
                            if data.get("password"):
                                django_user.set_password(data["password"])
                            django_user.save()

                            admin_group, _ = Group.objects.get_or_create(name="Admin")
                            django_user.groups.add(admin_group)
                        except Exception as e:
                            messages.warning(
                                request,
                                f"Admin updated, but failed to sync Django user: {e}",
                            )
                    elif self.model.__name__ == "Supplier":
                        old_email = obj.email
                        obj.name = data.get("name", obj.name)
                        obj.email = data.get("email", obj.email)
                        if data.get("password"):
                            obj.set_password(data["password"])
                        obj.save()
                        try:
                            from django.contrib.auth.models import (
                                User as DjangoUser,
                                Group,
                            )

                            django_user = (
                                DjangoUser.objects.filter(username=old_email).first()
                                or DjangoUser.objects.filter(username=obj.email).first()
                            )
                            if django_user is None:
                                django_user = DjangoUser(
                                    username=obj.email, email=obj.email
                                )
                            django_user.username = obj.email
                            django_user.email = obj.email
                            django_user.first_name = obj.name
                            django_user.is_staff = False
                            django_user.is_superuser = False
                            if data.get("password"):
                                django_user.set_password(data["password"])
                            django_user.save()

                            supplier_group, _ = Group.objects.get_or_create(
                                name="Supplier"
                            )
                            django_user.groups.add(supplier_group)
                        except Exception as e:
                            messages.warning(
                                request,
                                f"Supplier updated, but failed to sync Django user: {e}",
                            )
                        grocery_id = data.get("grocery_id")
                        if grocery_id is not None:
                            try:
                                new_grocery = Grocery.nodes.get(uid=grocery_id)
                                existing = obj.responsible_for.single()
                                if existing:
                                    obj.responsible_for.disconnect(existing)
                                obj.responsible_for.connect(new_grocery)
                            except Grocery.DoesNotExist:
                                pass
                    elif self.model.__name__ == "Item":
                        obj.name = data.get("name", obj.name)
                        obj.item_type = data.get("item_type", obj.item_type)
                        obj.item_location = data.get("item_location", obj.item_location)
                        if data.get("price") is not None:
                            obj.price = data["price"]
                        obj.save()
                        try:
                            from django.contrib.auth.models import Group

                            is_sup = Group.objects.filter(
                                user=request.user, name="Supplier"
                            ).exists()
                        except Exception:
                            is_sup = False
                        if not is_sup:
                            grocery_id = data.get("grocery_id")
                            if grocery_id:
                                try:
                                    current = obj.belongs_to_grocery.single()
                                    if current and current.uid != grocery_id:
                                        current.items.disconnect(obj)
                                    new_grocery = Grocery.nodes.get(uid=grocery_id)
                                    new_grocery.items.connect(obj)
                                except Grocery.DoesNotExist:
                                    pass
                    elif self.model.__name__ == "DailyIncome":
                        if data.get("date"):
                            obj.date = data["date"]
                        if data.get("amount") is not None:
                            obj.amount = data["amount"]
                        obj.save()
                        try:
                            from django.contrib.auth.models import Group

                            is_sup = Group.objects.filter(
                                user=request.user, name="Supplier"
                            ).exists()
                        except Exception:
                            is_sup = False
                        if not is_sup:
                            grocery_id = data.get("grocery_id")
                            if grocery_id:
                                try:
                                    current = obj.grocery.single()
                                    if current and current.uid != grocery_id:
                                        current.daily_incomes.disconnect(obj)
                                    new_grocery = Grocery.nodes.get(uid=grocery_id)
                                    new_grocery.daily_incomes.connect(obj)
                                except Grocery.DoesNotExist:
                                    pass
                    messages.success(
                        request, f"{self.model.__name__} updated successfully"
                    )
                    return redirect("../../")
                except Exception as e:
                    messages.error(
                        request, f"Error updating {self.model.__name__}: {e}"
                    )
        else:
            form = FormClass(initial=initial)

        context = {
            "title": f"Edit {self.model.__name__}",
            "form": form,
            "model_name": self.model.__name__,
            "object_id": object_id,
        }
        return render(request, "admin/neo4j_form.html", context)

    def delete_view(self, request, object_id):
        def is_supplier(u):
            try:
                from django.contrib.auth.models import Group

                return (
                    u.is_active
                    and Group.objects.filter(user=u, name="Supplier").exists()
                )
            except Exception:
                return False

        def is_admin(u):
            return u.is_active and (u.is_staff or u.is_superuser)

        model_name = self.model.__name__
        if not (
            is_admin(request.user)
            or (is_supplier(request.user) and model_name in ["Item", "DailyIncome"])
        ):
            messages.error(request, "You don't have permission to delete records.")
            return redirect("/admin/")

        try:
            obj = self.model.nodes.get(uid=object_id)
            if self.model.__name__ == "Item":
                obj.soft_delete()
            elif self.model.__name__ in ["Grocery", "Admin", "Supplier"]:
                if hasattr(obj, "is_active"):
                    obj.is_active = False
                    obj.save()
                if self.model.__name__ == "Supplier":
                    try:
                        from django.contrib.auth.models import User as DjangoUser

                        django_user = DjangoUser.objects.filter(
                            username=obj.email
                        ).first()
                        if django_user:
                            django_user.is_active = False
                            django_user.save()
                    except Exception:
                        pass
                if self.model.__name__ == "Admin":
                    try:
                        from django.contrib.auth.models import User as DjangoUser

                        django_user = DjangoUser.objects.filter(
                            username=obj.email
                        ).first()
                        if django_user:
                            django_user.is_active = False
                            django_user.save()
                    except Exception:
                        pass
            else:
                messages.warning(request, "Delete action not supported for this model")
                return redirect("../")
            messages.success(request, "Record deleted (soft) successfully")
        except Exception as e:
            messages.error(request, f"Error deleting record: {e}")
        return redirect("../../")


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
                "admins/add/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).add_view),
                name="neo4j_admin_add",
            ),
            path(
                "admins/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).change_view),
                name="neo4j_admin_change",
            ),
            path(
                "admins/<str:object_id>/edit/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).edit_view),
                name="neo4j_admin_edit",
            ),
            path(
                "admins/<str:object_id>/delete/",
                self.admin_view(Neo4jModelAdmin(Neo4jAdmin, self).delete_view),
                name="neo4j_admin_delete",
            ),
            path(
                "suppliers/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).changelist_view),
                name="neo4j_supplier_changelist",
            ),
            path(
                "suppliers/add/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).add_view),
                name="neo4j_supplier_add",
            ),
            path(
                "suppliers/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).change_view),
                name="neo4j_supplier_change",
            ),
            path(
                "suppliers/<str:object_id>/edit/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).edit_view),
                name="neo4j_supplier_edit",
            ),
            path(
                "suppliers/<str:object_id>/delete/",
                self.admin_view(Neo4jModelAdmin(Supplier, self).delete_view),
                name="neo4j_supplier_delete",
            ),
            path(
                "groceries/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).changelist_view),
                name="neo4j_grocery_changelist",
            ),
            path(
                "groceries/add/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).add_view),
                name="neo4j_grocery_add",
            ),
            path(
                "groceries/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).change_view),
                name="neo4j_grocery_change",
            ),
            path(
                "groceries/<str:object_id>/edit/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).edit_view),
                name="neo4j_grocery_edit",
            ),
            path(
                "groceries/<str:object_id>/delete/",
                self.admin_view(Neo4jModelAdmin(Grocery, self).delete_view),
                name="neo4j_grocery_delete",
            ),
            path(
                "items/",
                self.admin_view(Neo4jModelAdmin(Item, self).changelist_view),
                name="neo4j_item_changelist",
            ),
            path(
                "items/add/",
                self.admin_view(Neo4jModelAdmin(Item, self).add_view),
                name="neo4j_item_add",
            ),
            path(
                "items/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(Item, self).change_view),
                name="neo4j_item_change",
            ),
            path(
                "items/<str:object_id>/edit/",
                self.admin_view(Neo4jModelAdmin(Item, self).edit_view),
                name="neo4j_item_edit",
            ),
            path(
                "items/<str:object_id>/delete/",
                self.admin_view(Neo4jModelAdmin(Item, self).delete_view),
                name="neo4j_item_delete",
            ),
            path(
                "daily-income/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).changelist_view),
                name="neo4j_dailyincome_changelist",
            ),
            path(
                "daily-income/add/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).add_view),
                name="neo4j_dailyincome_add",
            ),
            path(
                "daily-income/<str:object_id>/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).change_view),
                name="neo4j_dailyincome_change",
            ),
            path(
                "daily-income/<str:object_id>/edit/",
                self.admin_view(Neo4jModelAdmin(DailyIncome, self).edit_view),
                name="neo4j_dailyincome_edit",
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
        try:
            from django.contrib.auth.models import Group

            is_supplier = Group.objects.filter(
                user=request.user, name="Supplier"
            ).exists()
        except Exception:
            is_supplier = False

        if is_supplier:
            menu = [
                {"name": "Items", "url": "admin:neo4j_item_changelist"},
                {"name": "Daily Income", "url": "admin:neo4j_dailyincome_changelist"},
            ]
        else:
            menu = [
                {"name": "Admins", "url": "admin:neo4j_admin_changelist"},
                {"name": "Suppliers", "url": "admin:neo4j_supplier_changelist"},
                {"name": "Groceries", "url": "admin:neo4j_grocery_changelist"},
                {"name": "Items", "url": "admin:neo4j_item_changelist"},
                {"name": "Daily Income", "url": "admin:neo4j_dailyincome_changelist"},
                {"name": "Database Stats", "url": "admin:neo4j_stats"},
            ]

        extra_context["neo4j_models"] = menu
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

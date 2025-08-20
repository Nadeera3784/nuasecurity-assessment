from typing import Optional, List

from .models import Admin as Neo4jAdmin, Supplier, Grocery


def is_supplier_user(user) -> bool:
    try:
        from django.contrib.auth.models import Group

        return (
            getattr(user, "is_active", False)
            and Group.objects.filter(user=user, name="Supplier").exists()
        )
    except Exception:
        return False


def is_admin_user(user) -> bool:
    try:
        from django.contrib.auth.models import Group

        in_supplier_group = Group.objects.filter(user=user, name="Supplier").exists()
    except Exception:
        in_supplier_group = False
    return (
        getattr(user, "is_active", False)
        and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
        and not in_supplier_group
    )


def get_login_email(user) -> Optional[str]:
    return getattr(user, "email", None) or getattr(user, "username", None)


def get_supplier_grocery_for_user(user) -> Optional[Grocery]:
    try:
        login_email = get_login_email(user)
        if not login_email:
            return None
        supplier_node = Supplier.nodes.get(email=login_email)
        return supplier_node.responsible_for.single()
    except Exception:
        return None


def filter_objects_for_supplier(objects: List, model_name: str, user) -> List:
    supplier_grocery = get_supplier_grocery_for_user(user)
    if not supplier_grocery:
        return []

    filtered = []
    if model_name == "Item":
        for it in objects:
            try:
                g = it.belongs_to_grocery.single()
                if g and g.uid == supplier_grocery.uid:
                    filtered.append(it)
            except Exception:
                continue
    elif model_name == "DailyIncome":
        for inc in objects:
            try:
                g = inc.grocery.single()
                if g and g.uid == supplier_grocery.uid:
                    filtered.append(inc)
            except Exception:
                continue
    return filtered


def sync_django_user_for_admin(admin_node: Neo4jAdmin, raw_password: str) -> None:
    try:
        from django.contrib.auth.models import User as DjangoUser, Group

        django_user, _ = DjangoUser.objects.get_or_create(
            username=admin_node.email, defaults={"email": admin_node.email}
        )
        django_user.username = admin_node.email
        django_user.email = admin_node.email
        django_user.first_name = admin_node.name
        django_user.is_active = True
        django_user.is_staff = True
        django_user.is_superuser = True
        if raw_password:
            django_user.set_password(raw_password)
        django_user.save()

        admin_group, _ = Group.objects.get_or_create(name="Admin")
        django_user.groups.add(admin_group)
    except Exception:
        pass


def sync_django_user_for_supplier(supplier_node: Supplier, raw_password: str) -> None:
    try:
        from django.contrib.auth.models import User as DjangoUser, Group

        django_user, _ = DjangoUser.objects.get_or_create(
            username=supplier_node.email, defaults={"email": supplier_node.email}
        )
        django_user.username = supplier_node.email
        django_user.email = supplier_node.email
        django_user.first_name = supplier_node.name
        django_user.is_active = True
        django_user.is_staff = False
        django_user.is_superuser = False
        if raw_password:
            django_user.set_password(raw_password)
        django_user.save()

        supplier_group, _ = Group.objects.get_or_create(name="Supplier")
        django_user.groups.add(supplier_group)
    except Exception:
        pass


def deactivate_django_user_by_email(email: str) -> None:
    try:
        from django.contrib.auth.models import User as DjangoUser

        django_user = DjangoUser.objects.filter(username=email).first()
        if django_user:
            django_user.is_active = False
            django_user.save()
    except Exception:
        pass


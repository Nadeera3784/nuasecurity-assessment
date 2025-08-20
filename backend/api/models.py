from neomodel import (
    StructuredNode,
    StringProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    FloatProperty,
    BooleanProperty,
    UniqueIdProperty,
    EmailProperty,
    ZeroOrOne,
)
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime


class BaseNode(StructuredNode):
    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    def save(self):
        self.updated_at = datetime.now()
        super().save()

    class Meta:
        abstract = True


class User(BaseNode):
    name = StringProperty(required=True)
    email = EmailProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    user_type = StringProperty(
        required=True, choices=[("admin", "Admin"), ("supplier", "Supplier")]
    )
    is_active = BooleanProperty(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Admin(User):
    manages_groceries = RelationshipTo("Grocery", "MANAGES")

    def save(self):
        self.user_type = "admin"
        super().save()


class Supplier(User):
    responsible_for = RelationshipTo(
        "Grocery", "RESPONSIBLE_FOR", cardinality=ZeroOrOne
    )
    added_items = RelationshipTo("Item", "ADDED_ITEM")
    recorded_incomes = RelationshipTo("DailyIncome", "RECORDED_INCOME")

    def save(self):
        self.user_type = "supplier"
        super().save()


class Grocery(BaseNode):
    name = StringProperty(required=True)
    location = StringProperty(required=True)
    is_active = BooleanProperty(default=True)

    managed_by = RelationshipFrom("Admin", "MANAGES")
    supplier = RelationshipFrom("Supplier", "RESPONSIBLE_FOR", cardinality=ZeroOrOne)
    items = RelationshipTo("Item", "HAS_ITEM")
    daily_incomes = RelationshipTo("DailyIncome", "HAS_INCOME")

    def __str__(self):
        return f"{self.name} - {self.location}"


class Item(BaseNode):
    name = StringProperty(required=True)
    item_type = StringProperty(required=True)
    item_location = StringProperty(required=True)
    price = FloatProperty(required=True)
    is_deleted = BooleanProperty(default=False)

    belongs_to_grocery = RelationshipFrom("Grocery", "HAS_ITEM")
    added_by = RelationshipFrom("Supplier", "ADDED_ITEM")

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return f"{self.name} - {self.item_type} - ${self.price}"


class DailyIncome(BaseNode):
    date = DateTimeProperty(required=True)
    amount = FloatProperty(required=True)

    grocery = RelationshipFrom("Grocery", "HAS_INCOME")
    recorded_by = RelationshipFrom("Supplier", "RECORDED_INCOME")

    def __str__(self):
        return f"Income: ${self.amount} on {self.date}"

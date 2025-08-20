from rest_framework import serializers
from .models import Admin, Supplier, Grocery, Item, DailyIncome


class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        from .models import User

        try:
            existing_user = User.nodes.get(email=value)
            if existing_user:
                raise serializers.ValidationError(
                    "User with this email already exists."
                )
        except User.DoesNotExist:
            pass
        return value


class AdminRegistrationSerializer(UserRegistrationSerializer):
    def create(self, validated_data):
        admin = Admin()
        admin.name = validated_data["name"]
        admin.email = validated_data["email"]
        admin.set_password(validated_data["password"])
        admin.save()
        return admin


class SupplierRegistrationSerializer(UserRegistrationSerializer):
    grocery_id = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        grocery_id = validated_data.pop("grocery_id", None)
        supplier = Supplier()
        supplier.name = validated_data["name"]
        supplier.email = validated_data["email"]
        supplier.set_password(validated_data["password"])
        supplier.save()

        if grocery_id:
            try:
                grocery = Grocery.nodes.get(uid=grocery_id)
                supplier.responsible_for.connect(grocery)
            except Grocery.DoesNotExist:
                pass

        return supplier


class UserSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField()
    email = serializers.EmailField()
    user_type = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class GrocerySerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=200)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    supplier_name = serializers.SerializerMethodField()

    def get_supplier_name(self, obj):
        try:
            supplier = obj.supplier.single()
            return supplier.name if supplier else None
        except:
            return None

    def create(self, validated_data):
        grocery = Grocery()
        grocery.name = validated_data["name"]
        grocery.location = validated_data["location"]
        grocery.is_active = validated_data.get("is_active", True)
        grocery.save()
        return grocery

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.location = validated_data.get("location", instance.location)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance


class ItemSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    item_type = serializers.CharField(max_length=50)
    item_location = serializers.CharField(max_length=100)
    price = serializers.FloatField(min_value=0)
    is_deleted = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    grocery_name = serializers.SerializerMethodField()
    added_by_name = serializers.SerializerMethodField()

    def get_grocery_name(self, obj):
        try:
            grocery = obj.belongs_to_grocery.single()
            return grocery.name if grocery else None
        except:
            return None

    def get_added_by_name(self, obj):
        try:
            supplier = obj.added_by.single()
            return supplier.name if supplier else None
        except:
            return None

    def create(self, validated_data):
        item = Item()
        item.name = validated_data["name"]
        item.item_type = validated_data["item_type"]
        item.item_location = validated_data["item_location"]
        item.price = validated_data["price"]
        item.save()
        return item

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.item_type = validated_data.get("item_type", instance.item_type)
        instance.item_location = validated_data.get(
            "item_location", instance.item_location
        )
        instance.price = validated_data.get("price", instance.price)
        instance.save()
        return instance


class DailyIncomeSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    date = serializers.DateTimeField()
    amount = serializers.FloatField(min_value=0)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    grocery_name = serializers.SerializerMethodField()
    recorded_by_name = serializers.SerializerMethodField()

    def get_grocery_name(self, obj):
        try:
            grocery = obj.grocery.single()
            return grocery.name if grocery else None
        except:
            return None

    def get_recorded_by_name(self, obj):
        try:
            supplier = obj.recorded_by.single()
            return supplier.name if supplier else None
        except:
            return None

    def create(self, validated_data):
        income = DailyIncome()
        income.date = validated_data["date"]
        income.amount = validated_data["amount"]
        income.save()
        return income

    def update(self, instance, validated_data):
        instance.date = validated_data.get("date", instance.date)
        instance.amount = validated_data.get("amount", instance.amount)
        instance.save()
        return instance


class GroceryDetailSerializer(GrocerySerializer):
    items_count = serializers.SerializerMethodField()
    total_income = serializers.SerializerMethodField()

    def get_items_count(self, obj):
        try:
            return len([item for item in obj.items.all() if not item.is_deleted])
        except:
            return 0

    def get_total_income(self, obj):
        try:
            incomes = obj.daily_incomes.all()
            return sum(income.amount for income in incomes)
        except:
            return 0

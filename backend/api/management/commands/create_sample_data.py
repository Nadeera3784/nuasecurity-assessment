"""
Management command to create sample data for testing.
"""

from django.core.management.base import BaseCommand
from api.models import Admin, Supplier, Grocery, Item, DailyIncome
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Create sample data for testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        try:
            # Create sample admin
            admin = Admin()
            admin.name = "Super Admin"
            admin.email = "admin@grocery.com"
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(f"Created admin: {admin.email}")

            # Create sample groceries
            grocery1 = Grocery()
            grocery1.name = "Downtown Grocery"
            grocery1.location = "123 Main Street, Downtown"
            grocery1.save()
            admin.manages_groceries.connect(grocery1)

            grocery2 = Grocery()
            grocery2.name = "Uptown Market"
            grocery2.location = "456 Oak Avenue, Uptown"
            grocery2.save()
            admin.manages_groceries.connect(grocery2)

            self.stdout.write(f"Created groceries: {grocery1.name}, {grocery2.name}")

            # Create sample suppliers
            supplier1 = Supplier()
            supplier1.name = "John Doe"
            supplier1.email = "john@grocery.com"
            supplier1.set_password("supplier123")
            supplier1.save()
            supplier1.responsible_for.connect(grocery1)

            supplier2 = Supplier()
            supplier2.name = "Jane Smith"
            supplier2.email = "jane@grocery.com"
            supplier2.set_password("supplier123")
            supplier2.save()
            supplier2.responsible_for.connect(grocery2)

            self.stdout.write(
                f"Created suppliers: {supplier1.email}, {supplier2.email}"
            )

            # Create sample items
            items_data = [
                {
                    "name": "Apples",
                    "type": "food",
                    "location": "first floor",
                    "price": 2.99,
                    "grocery": grocery1,
                    "supplier": supplier1,
                },
                {
                    "name": "Bananas",
                    "type": "food",
                    "location": "first floor",
                    "price": 1.99,
                    "grocery": grocery1,
                    "supplier": supplier1,
                },
                {
                    "name": "Chess Set",
                    "type": "game",
                    "location": "second floor",
                    "price": 29.99,
                    "grocery": grocery1,
                    "supplier": supplier1,
                },
                {
                    "name": "Oranges",
                    "type": "food",
                    "location": "first floor",
                    "price": 3.49,
                    "grocery": grocery2,
                    "supplier": supplier2,
                },
                {
                    "name": "Board Game",
                    "type": "game",
                    "location": "second floor",
                    "price": 19.99,
                    "grocery": grocery2,
                    "supplier": supplier2,
                },
            ]

            for item_data in items_data:
                item = Item()
                item.name = item_data["name"]
                item.item_type = item_data["type"]
                item.item_location = item_data["location"]
                item.price = item_data["price"]
                item.save()

                # Connect relationships
                item_data["grocery"].items.connect(item)
                item_data["supplier"].added_items.connect(item)

                self.stdout.write(f"Created item: {item.name}")

            # Create sample daily income records
            base_date = datetime.now() - timedelta(days=7)
            for i in range(7):
                # Income for grocery1
                income1 = DailyIncome()
                income1.date = base_date + timedelta(days=i)
                income1.amount = 150.0 + (i * 20)
                income1.save()
                grocery1.daily_incomes.connect(income1)
                supplier1.recorded_incomes.connect(income1)

                # Income for grocery2
                income2 = DailyIncome()
                income2.date = base_date + timedelta(days=i)
                income2.amount = 200.0 + (i * 15)
                income2.save()
                grocery2.daily_incomes.connect(income2)
                supplier2.recorded_incomes.connect(income2)

            self.stdout.write("Created sample daily income records")

            self.stdout.write(
                self.style.SUCCESS("\nSample data created successfully!\n")
            )
            self.stdout.write("Admin login: admin@grocery.com / admin123")
            self.stdout.write("Supplier 1 login: john@grocery.com / supplier123")
            self.stdout.write("Supplier 2 login: jane@grocery.com / supplier123")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating sample data: {str(e)}"))

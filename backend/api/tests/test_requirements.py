from datetime import datetime, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from neomodel import db

from api.models import Admin, Supplier, Grocery, Item
from api.authentication import create_jwt_token


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        # TODO: state leakage
        self._clear_graph()

        self.admin = Admin(name="Admin A", email="admin@example.com")
        self.admin.set_password("adminpass123")
        self.admin.save()

        self.supplier1 = Supplier(name="Supplier One", email="sup1@example.com")
        self.supplier1.set_password("supplierpass1")
        self.supplier1.save()

        self.supplier2 = Supplier(name="Supplier Two", email="sup2@example.com")
        self.supplier2.set_password("supplierpass2")
        self.supplier2.save()

        self.grocery1 = Grocery(name="Fresh Mart", location="Downtown")
        self.grocery1.save()
        self.grocery2 = Grocery(name="Daily Goods", location="Uptown")
        self.grocery2.save()

        self.supplier1.responsible_for.connect(self.grocery1)

        self.admin.manages_groceries.connect(self.grocery1)
        self.admin.manages_groceries.connect(self.grocery2)

        self.other_item = Item(
            name="Chess Board",
            item_type="game",
            item_location="second roof",
            price=30.0,
        )
        self.other_item.save()
        self.grocery2.items.connect(self.other_item)

        self.admin_headers = self._auth_headers_for(self.admin)
        self.supplier1_headers = self._auth_headers_for(self.supplier1)
        self.supplier2_headers = self._auth_headers_for(self.supplier2)

    def tearDown(self):
        super().tearDown()
        self._clear_graph()

    def _clear_graph(self):
        db.cypher_query("MATCH (n) DETACH DELETE n")

    def _auth_headers_for(self, user):
        tokens = create_jwt_token(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}


class RequirementsTestCase(BaseAPITestCase):
    def test_authentication_required(self):
        url = reverse("grocery-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(url, **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_and_manage_grocery_and_supplier(self):
        create_url = reverse("grocery-list")
        payload = {"name": "Budget Shop", "location": "Midtown"}
        response = self.client.post(
            create_url, payload, format="json", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        grocery_id = response.data["uid"]

        update_url = reverse("grocery-detail", args=[grocery_id])
        response = self.client.put(
            update_url, {"location": "New Midtown"}, format="json", **self.admin_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["location"], "New Midtown")

        response = self.client.delete(update_url, **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("register_supplier")
        payload = {
            "name": "New Supplier",
            "email": "new@sup.com",
            "password": "newsupplier123",
        }
        response = self.client.post(url, payload, format="json", **self.admin_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "new@sup.com")

    def test_supplier_cannot_manage_other_grocery_items_but_can_read(self):
        url = reverse("item-list")
        payload = {
            "name": "Apple",
            "item_type": "food",
            "item_location": "first roof",
            "price": 2.5,
            "grocery_id": self.grocery2.uid,
        }
        response = self.client.post(
            url, payload, format="json", **self.supplier1_headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        list_resp = self.client.get(url, **self.supplier1_headers)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_resp.data), 1)

        payload["grocery_id"] = self.grocery1.uid
        response = self.client.post(
            url, payload, format="json", **self.supplier1_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        own_item_id = response.data["uid"]

        detail_url = reverse("item-detail", args=[own_item_id])
        response = self.client.put(
            detail_url, {"price": 3.0}, format="json", **self.supplier2_headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(detail_url, **self.supplier2_headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_soft_delete_item(self):
        create_item_url = reverse("item-list")
        payload = {
            "name": "Milk",
            "item_type": "food",
            "item_location": "first roof",
            "price": 4.5,
            "grocery_id": self.grocery1.uid,
        }
        resp = self.client.post(
            create_item_url, payload, format="json", **self.admin_headers
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.data["uid"]

        detail_url = reverse("item-detail", args=[item_id])
        del_resp = self.client.delete(detail_url, **self.admin_headers)
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)

        get_resp = self.client.get(detail_url, **self.admin_headers)
        self.assertEqual(get_resp.status_code, status.HTTP_404_NOT_FOUND)

        item_node = Item.nodes.get(uid=item_id)
        self.assertTrue(item_node.is_deleted)

        list_resp = self.client.get(create_item_url, **self.admin_headers)
        self.assertTrue(all(i["uid"] != item_id for i in list_resp.data))

    def test_daily_income_permissions_and_aggregation(self):
        income_url = reverse("dailyincome-list")
        now = datetime.utcnow()
        payload = {"date": now.isoformat() + "Z", "amount": 100.0}
        resp = self.client.post(
            income_url, payload, format="json", **self.supplier1_headers
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        income_id = resp.data["uid"]

        payload2 = {
            "date": (now + timedelta(days=1)).isoformat() + "Z",
            "amount": 55.0,
            "grocery_id": self.grocery2.uid,
        }
        resp2 = self.client.post(
            income_url, payload2, format="json", **self.admin_headers
        )
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        other_income_id = resp2.data["uid"]

        other_detail = reverse("dailyincome-detail", args=[other_income_id])
        forb = self.client.get(other_detail, **self.supplier1_headers)
        self.assertEqual(forb.status_code, status.HTTP_403_FORBIDDEN)

        list_all = self.client.get(income_url, **self.admin_headers)
        self.assertEqual(list_all.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_all.data), 2)

        grocery_detail_url = reverse("grocery-detail", args=[self.grocery1.uid])
        detail_resp = self.client.get(grocery_detail_url, **self.admin_headers)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertIn("items_count", detail_resp.data)
        self.assertIn("total_income", detail_resp.data)

    def test_admin_manage_user_accounts_and_supplier_income_visibility(self):
        user_detail_url = reverse("user-detail", args=[self.supplier2.uid])
        resp = self.client.put(
            user_detail_url,
            {"name": "Supplier Two Updated"},
            format="json",
            **self.admin_headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Supplier Two Updated")

        del_resp = self.client.delete(user_detail_url, **self.admin_headers)
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)

        income_url = reverse("dailyincome-list")
        now = datetime.utcnow()

        self.client.post(
            income_url,
            {"date": now.isoformat() + "Z", "amount": 25.0},
            format="json",
            **self.supplier1_headers,
        )

        self.client.post(
            income_url,
            {
                "date": now.isoformat() + "Z",
                "amount": 40.0,
                "grocery_id": self.grocery2.uid,
            },
            format="json",
            **self.admin_headers,
        )

        sup_list = self.client.get(income_url, **self.supplier1_headers)
        self.assertEqual(sup_list.status_code, status.HTTP_200_OK)

        grocery_names = {rec.get("grocery_name") for rec in sup_list.data}
        self.assertSetEqual(grocery_names, {self.grocery1.name})

    def test_updated_at_changes_on_update_and_delete(self):
        url = reverse("item-list")
        payload = {
            "name": "Bread",
            "item_type": "food",
            "item_location": "first roof",
            "price": 1.5,
            "grocery_id": self.grocery1.uid,
        }
        resp = self.client.post(url, payload, format="json", **self.admin_headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.data["uid"]

        item_detail = reverse("item-detail", args=[item_id])
        get1 = self.client.get(item_detail, **self.admin_headers)
        self.assertEqual(get1.status_code, status.HTTP_200_OK)
        first_updated_at = get1.data["updated_at"]

        patch_resp = self.client.put(
            item_detail, {"price": 1.75}, format="json", **self.admin_headers
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        second_updated_at = patch_resp.data["updated_at"]
        self.assertNotEqual(first_updated_at, second_updated_at)

        del_resp = self.client.delete(item_detail, **self.admin_headers)
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)

        list_resp = self.client.get(url, **self.admin_headers)
        self.assertTrue(all(i["uid"] != item_id for i in list_resp.data))

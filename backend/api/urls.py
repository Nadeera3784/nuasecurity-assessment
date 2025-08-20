from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"groceries", views.GroceryViewSet, basename="grocery")
router.register(r"items", views.ItemViewSet, basename="item")
router.register(r"daily-income", views.DailyIncomeViewSet, basename="dailyincome")

urlpatterns = [
    path("auth/register/admin/", views.register_admin, name="register_admin"),
    path("auth/register/supplier/", views.register_supplier, name="register_supplier"),
    path("auth/login/", views.login, name="login"),
    path("auth/profile/", views.profile, name="profile"),
    path("", include(router.urls)),
]

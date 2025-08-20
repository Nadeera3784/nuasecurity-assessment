from django.contrib import admin
from django.urls import path, include
from api.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("django-admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

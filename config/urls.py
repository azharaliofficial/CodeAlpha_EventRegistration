from django.contrib import admin
from django.urls import include, path

from events import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("events.urls")),
    path("", views.home),
]

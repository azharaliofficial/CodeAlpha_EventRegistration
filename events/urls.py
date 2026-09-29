from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup),
    path("login/", views.login),
    path("events/", views.event_list),
    path("events/<int:event_id>/", views.event_detail),
    path("events/<int:event_id>/register/", views.register_for_event),
    path("my-registrations/", views.my_registrations),
    path("registrations/<int:registration_id>/", views.cancel_registration),
]

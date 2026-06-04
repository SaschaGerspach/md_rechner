from django.urls import path

from . import views

urlpatterns = [
    path("balance/", views.balance, name="balance"),
    path("buildings/", views.buildings, name="buildings"),
    path("chain/", views.chain, name="chain"),
]

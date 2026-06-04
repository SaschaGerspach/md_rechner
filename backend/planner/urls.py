from django.urls import path

from . import views

urlpatterns = [
    path("balance/", views.balance, name="balance"),
    path("chain/", views.chain, name="chain"),
]

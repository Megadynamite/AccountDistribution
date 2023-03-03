from django.urls import path

from . import views

urlpatterns = [
    path('revoke/<int:token>/', views.revoke)
]

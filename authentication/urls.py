from django.urls import path

from . import views

urlpatterns = [
    path('testauth', views.testauth),
    path('revoke/<int:token>/', views.revoke)
]

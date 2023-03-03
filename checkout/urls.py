from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('checkout/<str:account_type>/', views.checkout, name='checkout'),
    path('checkin/', views.checkin, name='checkout')
]

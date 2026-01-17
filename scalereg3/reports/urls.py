from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('sales_dashboard/', views.sales_dashboard,
         {'report_name': 'Sales Dashboard'}),
    path('payment_code_usage/', views.payment_code_usage,
         {'report_name': 'Payment Code Usage'}),
]

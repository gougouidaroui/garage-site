from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vehicle/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicle/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('backup/', views.backup_data, name='backup_data'),
]

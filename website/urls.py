from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cycle/add/', views.add_cycle, name='add_cycle'),
    path('cycle/modify/<str:cycle_id>/', views.modify_cycle, name='modify_cycle'),
    path('backup/', views.backup_data, name='backup_data'),
    path('search/', views.search_cycles, name='search_cycles'),
    path('api/cycle-images/<str:cycle_id>/', views.cycle_images, name='cycle_images'),
]

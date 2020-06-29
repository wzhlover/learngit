from django.urls import path, re_path
from . import views

app_name = 'df_cart'

urlpatterns = [
    path('', views.cart),
    re_path('add(\d+)_(\d+)/', views.add),
    re_path('edit(\d+)_(\d+)/', views.edit),
    re_path('delete(\d+)/', views.delete),
]
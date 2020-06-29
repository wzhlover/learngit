from django.urls import path, re_path
from . import views

app_name = 'df_goods'

urlpatterns = [
    path('', views.index),
    re_path('list(\d+)_(\d+)_(\d+)/', views.list),
    re_path('(\d+)/', views.detail),
]
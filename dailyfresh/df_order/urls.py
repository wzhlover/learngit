from django.urls import path, re_path
from . import views

app_name = 'df_user'

urlpatterns = [
    path('order/', views.order),
    path('pay/', views.pay),

]

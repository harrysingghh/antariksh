from rest_api import views
from django.urls import path,include


urlpatterns = [
    path('', views.mgb_cycle),
    path('send_data/', views.data_oper)

]

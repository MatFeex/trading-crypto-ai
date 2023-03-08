from django.contrib import admin
from django.urls import  path
from . import views

urlpatterns = [
    # urls for BOT
    path('',views.home, name="home"),
    path('user/login/', views.login_user, name="login" ),
    path('user/register/', views.register_user, name="register" ),
    path('trades',views.read_trades, name="trades")
]

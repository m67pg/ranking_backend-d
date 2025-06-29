from django.urls import path
from . import views

urlpatterns = [
    path('api/login', views.login_user),
    path('api/logout', views.logout_user),
    path('api/check_login', views.check_login_status),
]

#!/usr/bin/env python3.7
from django.urls import path
from . import views

urlpatterns = [
    path('api/influencers/all', views.get_all_influencers_by_region),
    path('api/influencers', views.get_influencers),
    path('api/upload_influencers', views.upload_influencers),
]

"""
test URL Configuration for juntagrico_custom_sub development using old subscription overview
"""
from django.urls import include, path

urlpatterns = [
    path('', include('testurls')),
    path('', include('juntagrico.downgrade.urls_1_5')),
    path('', include('juntagrico_custom_sub.downgrade.urls_1_5')),
]

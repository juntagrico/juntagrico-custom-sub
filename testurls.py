"""
test URL Configuration for juntagrico_custom_sub development
"""
from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('juntagrico_custom_sub.urls')),
    path('', include('juntagrico.urls')),
]

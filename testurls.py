"""
test URL Configuration for juntagrico_custom_sub development
"""
import juntagrico
from django.urls import include, re_path
from django.contrib import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('juntagrico_custom_sub.urls')),
    re_path(r'^', include('juntagrico.urls')),
    re_path(r'^$', juntagrico.views.home),
]

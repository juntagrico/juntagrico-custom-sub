"""
test URL Configuration for juntagrico_custom_sub development
"""
from django.conf.urls import include, url
from django.contrib import admin
import juntagrico
import juntagrico_custom_sub.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('juntagrico.urls')),
    url(r'^', include('juntagrico_custom_sub.urls')),
    url(r'^$', juntagrico.views.home),
]

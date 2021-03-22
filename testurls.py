"""
test URL Configuration for juntagrico_custom_sub development
"""
import juntagrico
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('juntagrico_custom_sub.urls')),
    url(r'^', include('juntagrico.urls')),
    url(r'^$', juntagrico.views.home),
]

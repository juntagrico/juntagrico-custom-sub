"""juntagrico_custom_sub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path

from juntagrico_custom_sub import views

urlpatterns = [
    url('^cs/subscription/change/content/(?P<subscription_id>.*?)/', views.subscription_content_edit),
    url('^cs/subscription/change/result/', views.content_edit_result, name='content_edit_result'),
    url('^cs/contentchangelist/', views.contentchangelist),
    url('^cs/signup/initialselect/', views.custom_sub_initial_select, name='custom_sub_initial_select'),
    url('^cs/content/change/(?P<subscription_id>.*?)/', views.activate_future_content),
    path('my/subscription/change/size/<int:subscription_id>/', views.size_change, name='size-change'),
    path('my/create/subscription/summary/', views.CustomCSSummaryView.as_view(), name='cs-summary'),
    path('my/create/subscription/', views.custom_cs_select_subscription, name='cs-subscription'),
]

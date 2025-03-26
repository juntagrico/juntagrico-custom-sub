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
from django.urls import path

from juntagrico_custom_sub import views

urlpatterns = [
    path('cs/subscription/change/content/<subscription_id>/', views.subscription_select_content,
         name='content_edit'),  # noqa: E501
    path('cs/subscription/change/result/<int:subscription_id>/', views.content_edit_result, name='content_edit_result'),
    path('cs/contentchangelist/', views.list_content_changes, name='content_change_list'),
    path('cs/signup/initialselect/', views.initial_select_content, name='custom_sub_initial_select'),
    path('cs/content/change/<subscription_id>/', views.activate_future_content),
    # urls overriden from core to make the management of custom composition of subscriptions possible
    path('my/create/subscription/summary/', views.CustomCSSummaryView.as_view(), name='cs-summary'),
    path('my/subpart/cancel/<int:part_id>/<int:subscription_id>/', views.cancel_part,
         name='part-cancel'),
    path('my/subscription/part/<int:part_id>/change', views.part_change, name='part-change'),
    path('my/subscription/<int:subscription_id>/order/', views.part_order, name='part-order'),
    path('my/subscription/<int:subscription_id>/order/extra/', views.part_order, {'extra': True},
         name='extra-order'),
]

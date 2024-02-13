""" include this if you include juntagrico.downgrade.urls_1_5
"""
from django.urls import path

from juntagrico_custom_sub.downgrade import views_1_5

urlpatterns = [
    # urls overriden from core to make the management of custom composition of subscriptions possible
    path('my/subscription/change/size/<int:subscription_id>/', views_1_5.size_change, name='size-change'),
]

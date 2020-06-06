from django.contrib import admin

from juntagrico.admins import BaseAdmin
from juntagrico_custom_sub import models as jcsm


class SubItemsInline(admin.TabularInline):
    model = jcsm.SubscriptionContentItem


class FutureSubItemsInline(admin.TabularInline):
    model = jcsm.SubscriptionContentFutureItem


class MandatoryProductInline(admin.TabularInline):
    model = jcsm.Product.mandatory_for_sizes.through


class SubscriptionContentAdmin(admin.ModelAdmin):
    inlines = [
        SubItemsInline, FutureSubItemsInline
    ]


class CustomDeliveryProductInline(admin.TabularInline):
    model = jcsm.CustomDeliveryProduct


class CustomDeliveryAdmin(admin.ModelAdmin):
    inlines = [
        CustomDeliveryProductInline
    ]


class CustomDeliveryProductAdmin(BaseAdmin):
    list_display = ['name', 'code', 'units']


admin.site.register(jcsm.Product, CustomDeliveryProductAdmin)
admin.site.register(jcsm.SubscriptionContent, SubscriptionContentAdmin)
admin.site.register(jcsm.CustomDelivery, CustomDeliveryAdmin)

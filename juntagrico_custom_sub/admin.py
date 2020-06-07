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
    list_display = ('subscription_id', 'get_member', 'get_email', 'get_depot_name')

    search_fields = [
         'subscription__primary_member__email',
         'subscription__primary_member__first_name',
         'subscription__primary_member__last_name',
         'subscription__depot__name']

    def get_member(self, obj):
        mem = obj.subscription.primary_member
        return f"{mem.last_name}, {mem.first_name}"

    get_member.short_description = 'Mitglied'
    get_member.admin_order_field = 'subscription__primary_member__last_name'

    def get_email(self, obj):
        return obj.subscription.primary_member.email

    get_email.short_description = 'E-Mail Mitglied'
    get_email.admin_order_field = 'subscription__primary_member__email'

    def get_depot_name(self, obj):
        return obj.subscription.depot.name

    get_depot_name.short_description = 'Depot'
    get_depot_name.admin_order_field = 'subscription__depot__name'

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

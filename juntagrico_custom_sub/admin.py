from django.contrib import admin
from juntagrico.admins import BaseAdmin
from juntagrico.entity.subtypes import SubscriptionSize
from juntagrico.util import addons

from juntagrico_custom_sub.entity.custom_delivery import CustomDelivery, CustomDeliveryProduct
from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent
from juntagrico_custom_sub.entity.subscription_content_future_item import SubscriptionContentFutureItem
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.entity.subscription_size_mandatory_products import SubscriptionSizeMandatoryProducts  # noqa: F401 avoid fields.E331 issue TODO?


class SubItemsInline(admin.TabularInline):
    model = SubscriptionContentItem


class FutureSubItemsInline(admin.TabularInline):
    model = SubscriptionContentFutureItem


class MandatoryProductInline(admin.TabularInline):
    model = Product.mandatory_for_sizes.through


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
    model = CustomDeliveryProduct


class CustomDeliveryAdmin(admin.ModelAdmin):
    inlines = [
        CustomDeliveryProductInline
    ]


class CustomDeliveryProductAdmin(BaseAdmin):
    list_display = ['name', 'code', 'units']


admin.site.register(Product, CustomDeliveryProductAdmin)
admin.site.register(SubscriptionContent, SubscriptionContentAdmin)
admin.site.register(CustomDelivery, CustomDeliveryAdmin)

# extend the inline of SubscriptionSize
addons.config.register_model_inline(SubscriptionSize, MandatoryProductInline)

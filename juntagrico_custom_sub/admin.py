from django.contrib import admin

from juntagrico_custom_sub.models import *

class SubItemsInline(admin.TabularInline):
    model = SubscriptionContentItem

class FutureSubItemsInline(admin.TabularInline):
    model = SubscriptionContentFutureItem

class MandatoryProductInline(admin.TabularInline):
    model = Product.mandatory_for_sizes.through

class SubscriptionContentAdmin(admin.ModelAdmin):
    inlines = [
        SubItemsInline,FutureSubItemsInline
    ]

    
class CustomDeliveryProductInline(admin.TabularInline):
    model = CustomDeliveryProduct
class CustomDeliveryAdmin(admin.ModelAdmin):
    inlines = [
        CustomDeliveryProductInline
    ]
admin.site.register(Product)
admin.site.register(SubscriptionContent,SubscriptionContentAdmin)
admin.site.register(CustomDelivery,CustomDeliveryAdmin)

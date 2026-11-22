from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from juntagrico.models import Subscription

from juntagrico_custom_sub.entity.product import Product


class SubscriptionContent(models.Model):
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, related_name="custom")

    def __str__(self):
        return "Inhalt von Abo " + str(self.subscription.id)

    @property
    def sorted_products(self):
        return self.products.order_by('product')

    @property
    def amounts_for_products(self):
        result = {}
        products = Product.objects.all().order_by('code')
        for prod in products:
            try:
                amount = self.products.get(product=prod).amount
                result[prod] = amount
            except ObjectDoesNotExist:
                result[prod] = 0
                pass
        return result

    @property
    def display_content(self):
        result = []
        for prod in self.products.all().order_by('product__code'):
            try:
                amount = prod.amount
                if (amount > 0):
                    result.append(str(int(
                        amount * prod.product.unit_multiplier * prod.product.units)) + " " + prod.product.unit_name + " " + strip_tags(
                        prod.product.name))
            except ObjectDoesNotExist:
                pass
        return result

    @property
    def display_future_content(self):
        result = []
        for prod in self.future_products.all().order_by('product__code'):
            try:
                amount = prod.amount
                if (amount > 0):
                    result.append(str(int(
                        amount * prod.product.unit_multiplier * prod.product.units)) + " " + prod.product.unit_name + " " + strip_tags(
                        prod.product.name))
            except ObjectDoesNotExist:
                pass
        return result

    @property
    def content_changed(self):
        # uses .all() so that prefetched items are reused
        current = {item.product_id: item.amount for item in self.products.all()}
        future = {item.product_id: item.amount for item in self.future_products.all()}
        return current != future

    class Meta:
        verbose_name = _('Abo Inhalt')
        verbose_name_plural = _('Abo Inhalte')

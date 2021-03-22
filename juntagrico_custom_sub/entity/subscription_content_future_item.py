from django.db import models

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent


class SubscriptionContentFutureItem(models.Model):
    subscription_content = models.ForeignKey(SubscriptionContent, on_delete=models.CASCADE,
                                             related_name="future_products")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.IntegerField()

    @property
    def display_amount(self):
        return self.amount * self.product.display_units

    @property
    def amount_base_units(self):
        return self.amount * self.product.units

    def __lt__(self, other):
        return self.product.code < other.product.code

    class Meta:
        unique_together = (("subscription_content", "product"),)

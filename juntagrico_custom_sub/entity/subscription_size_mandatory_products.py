from django.db import models
from juntagrico.entity.subtypes import SubscriptionSize

from juntagrico_custom_sub.entity.product import Product


class SubscriptionSizeMandatoryProducts(models.Model):
    subscription_size = models.ForeignKey(SubscriptionSize, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("subscription_size", "product")

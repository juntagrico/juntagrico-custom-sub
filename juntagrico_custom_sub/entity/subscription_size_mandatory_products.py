from django.db import models
from juntagrico.entity.subtypes import ProductSize

from juntagrico_custom_sub.entity.product import Product


class SubscriptionSizeMandatoryProducts(models.Model):
    subscription_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("subscription_size", "product")

from django.db import models

from juntagrico.entity.subtypes import SubscriptionBundle

from juntagrico_custom_sub.entity.product import Product


class SubscriptionBundleMandatoryProducts(models.Model):
    subscription_bundle = models.ForeignKey(SubscriptionBundle, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subscription_bundle', 'product'], name='unique_subscription_bundle_product'),
        ]

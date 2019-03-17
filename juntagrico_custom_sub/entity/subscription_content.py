from django.db import models
from juntagrico.models import Subscription
from juntagrico_custom_sub.entity.product import Product
from django.core.exceptions import ObjectDoesNotExist

class SubscriptionContent(models.Model):
    subscription = models.OneToOneField(Subscription,on_delete=models.CASCADE,related_name="content")
    def __str__(self):
        return "Inhalt von Abo "+ str(self.subscription.id)
    
    @property
    def sorted_products(self):
        return self.products.order_by('product')

    @property
    def amounts_for_products(self):
        result = []
        products = Product.objects.all().order_by('id')
        for prod in products:
            try:
                amount = self.products.get(product=prod).amount
                result.append(amount)
            except ObjectDoesNotExist:
                result.append(0)
                pass
        return result
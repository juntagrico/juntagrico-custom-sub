from django.db import models
from juntagrico.models import Subscription
from juntagrico_custom_sub.entity.product import Product

class SubscriptionContent(models.Model):
    subscription = models.ForeignKey(Subscription,on_delete=models.CASCADE,related_name="contents")
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    amount = models.IntegerField()
    @property
    def display_amount(self):
        return self.amount * self.product.display_units
    @property
    def amount_base_units(self):
        return self.amount * self.product.units
    def __str__(self):
        return "Abo "+ str(self.subscription.id) +" enthält "+str(self.display_amount)+" "+ self.product.unit_name+" "+str(self.product.name)
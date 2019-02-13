from django.db import models
from juntagrico.models import Subscription
from juntagrico_custom_sub.entity.product import Product

class SubscriptionContent(models.Model):
    subscription = models.OneToOneField(Subscription,on_delete=models.CASCADE,related_name="contents")
    
    def __str__(self):
        return "Inhalt von Abo "+ str(self.subscription.id)
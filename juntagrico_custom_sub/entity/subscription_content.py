from django.db import models
from juntagrico.models import Subscription
from juntagrico_custom_sub.entity.product import Product
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

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

    @property
    def display_content(self):
        result = []
        for prod in self.products.all():
            try:
                amount = prod.amount
                if (amount>0):
                    result.append(str(amount * prod.product.unit_multiplier * prod.product.units) +" " + prod.product.unit_name +" "+ prod.product.name)
            except ObjectDoesNotExist:
                pass
        return result
    
    @property
    def display_future_content(self):
        result = []
        for prod in self.future_products.all():
            try:
                amount = prod.amount
                if (amount>0):
                    result.append(str(amount * prod.product.unit_multiplier * prod.product.units) +" " + prod.product.unit_name +" "+ prod.product.name)
            except ObjectDoesNotExist:
                pass
        return result 

    @property
    def content_changed(self):
        changed = False
        products = Product.objects.all().order_by('id')
        for prod in products:
            if  not (self.products.filter(product=prod).exists()) and not (self.future_products.filter(product=prod).exists()):
                continue
            if (not self.products.filter(product=prod).exists()) or not (self.future_products.filter(product=prod).exists()):
                changed = True
                break
            if(self.products.get(product=prod).amount != self.future_products.get(product=prod).amount):
                changed = True
                break
        return changed
    class Meta:
        verbose_name = _('Abo Inhalt')
        verbose_name_plural = _('Abo Inhalte')
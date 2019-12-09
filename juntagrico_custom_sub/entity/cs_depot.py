from juntagrico.models import Depot
from juntagrico_custom_sub.models import Product
from django.db.models import Sum

class CsDepot(Depot):
    class Meta:
        proxy = True

    @property
    def product_totals(self):
        self.fill_active_subscription_cache()
        products = Product.objects.all().order_by('id')
        amount_of_product = {}
        for product in products:
            productAmount = self.subscription_cache.filter(content__products__product__id=product.id).aggregate(Sum('content__products__amount'))['content__products__amount__sum'] or 0
            amount_of_product[product] = productAmount
        return amount_of_product
from django.db.models import Sum
from juntagrico.entity.depot import Depot

from juntagrico.util.models import q_isactive
from juntagrico_custom_sub.entity.product import Product


class CsDepot(Depot):
    class Meta:
        proxy = True

    @property
    def product_totals(self):
        products = Product.objects.all().order_by('code')
        amount_of_product = {}
        for product in products:
            productAmount = \
                self.subscription_set.filter(q_isactive(), content__products__product__id=product.id).order_by('primary_member__first_name', 'primary_member__last_name').aggregate(
                    Sum('content__products__amount'))['content__products__amount__sum'] or 0
            amount_of_product[product] = productAmount
        return amount_of_product

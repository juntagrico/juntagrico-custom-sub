import datetime

from django.db.models import Sum
from juntagrico.entity.depot import Depot
from juntagrico.entity.subs import SubscriptionPart

from juntagrico_custom_sub.entity.product import Product


class CsDepot(Depot):
    class Meta:
        proxy = True

    def subscriptions_on(self, date=None):
        """
        subscriptions of this depot that get a delivery on the given date.
        SubscriptionPartQuerySet.active_on respects interval and offset of the subscription types.
        Extra parts are ignored, as they are not part of the custom content.
        """
        date = date or datetime.date.today()
        due_parts = SubscriptionPart.objects.is_normal().active_on(date)
        return self.subscription_set.active_on(date).filter(
            pk__in=due_parts.values('subscription_id')
        ).order_by('primary_member__first_name', 'primary_member__last_name')

    def product_totals_on(self, date=None):
        totals = dict(
            self.subscriptions_on(date).order_by()
            .values_list('custom__products__product')
            .annotate(total=Sum('custom__products__amount'))
        )
        return {
            product: totals.get(product.pk) or 0
            for product in Product.objects.all().order_by('code')
        }

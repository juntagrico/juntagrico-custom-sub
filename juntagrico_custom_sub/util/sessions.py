from juntagrico.util import sessions

from juntagrico_custom_sub.entity.subscription_content_future_item import SubscriptionContentFutureItem
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.views import add_products_to_subscription


class SignupManager(sessions.SignupManager):
    def apply_subscriptions(self, member, co_members):
        subscription = super().apply_subscriptions(member, co_members)
        if subscription is not None:
            # create custom products
            custom_prod = self.get('custom_products')
            # associate custom products with subscription
            add_products_to_subscription(subscription.id, custom_prod, SubscriptionContentItem)
            add_products_to_subscription(subscription.id, custom_prod, SubscriptionContentFutureItem)
        return subscription

    def get_next_page(self):
        next_page = super().get_next_page()
        if next_page == 'cs-depot' and self.get('custom_products') is None:
            return 'custom_sub_initial_select'
        return next_page

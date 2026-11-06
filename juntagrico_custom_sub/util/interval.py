"""
Delivery rhythm handling.

juntagrico lets a SubscriptionType define an ``interval`` (deliver every n-th week) and an ``offset``.
The custom content of a subscription however belongs to the whole subscription and not to its parts.
Therefore, all (non-extra) parts of a subscription must share the same rhythm, otherwise it is not defined
what is delivered in a given week.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from juntagrico.config import Config


def rhythm(subscription_type):
    """
    normalized (interval, offset) tuple. Types with the same rhythm are delivered in the same weeks.
    """
    interval = subscription_type.interval or 1
    return interval, subscription_type.offset % interval


def rhythms(subscription_types):
    return {rhythm(t) for t in subscription_types if not t.is_extra}


def check_consistent_rhythm(subscription_types):
    if len(rhythms(subscription_types)) > 1:
        raise ValidationError(
            _('Alle Bestandteile eines {subscription}s müssen im gleichen Rhythmus geliefert werden.').format(
                subscription=Config.vocabulary('subscription')
            ),
            code='inconsistent_rhythm'
        )


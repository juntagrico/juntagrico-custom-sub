from django.shortcuts import get_object_or_404, redirect, render

from juntagrico.config import Config
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.view_decorators import primary_member_of_subscription
from juntagrico.entity.subs import Subscription
from juntagrico.util import temporal
from juntagrico.util.management import create_subscription_parts

from juntagrico.forms import SubscriptionPartOrderForm


@primary_member_of_subscription
def size_change(request, subscription_id):
    """
    Overriden from core
    change the size of a subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    if request.method == 'POST':
        form = SubscriptionPartOrderForm(subscription, request.POST)
        if form.is_valid():
            create_subscription_parts(subscription, form.get_selected(), True)
            return redirect("content_edit", subscription_id=subscription_id)
    else:
        form = SubscriptionPartOrderForm()
    renderdict = {
        'form': form,
        'subscription': subscription,
        'hours_used': Config.assignment_unit() == 'HOURS',
        'next_cancel_date': temporal.next_cancelation_date(),
        'parts_order_allowed': not subscription.canceled,
        'can_change_part': SubscriptionTypeDao.get_normal_visible().count() > 1
    }
    return render(request, 'size_change.html', renderdict)

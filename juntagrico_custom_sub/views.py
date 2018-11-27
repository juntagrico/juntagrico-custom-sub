from django.contrib.auth.decorators import login_required

from django.shortcuts import render,get_object_or_404
from juntagrico_custom_sub.models import *
from juntagrico.models import *
from django.db.models import Sum

import json
import logging

logger = logging.getLogger(__name__)

def subscription_content(request,subscription_id=None):
    returnValues = dict()
    member = request.user.member
    future_subscription = member.future_subscription is not None
    if subscription_id is None:
        subscription = member.subscription
    else:
        subscription = get_object_or_404(Subscription, id=subscription_id)
        future_subscription = future_subscription and not(
            subscription == member.future_subscription)
    if "addProduct" in request.POST:
        productId = request.POST["product_id"]
        product = Product.objects.get(id=productId)
        productAmount = int(request.POST["product_amount"])
        if is_subscription_content_valid(subscription,product,productAmount):
            returnValues['error'] = "Dein Abo hat nicht genug Platz für weitere Produkte"
        else:
            productContent = SubscriptionContent(amount=productAmount,product=product,subscription=subscription)
            productContent.save()
    if "removeProduct" in request.POST:
        content = SubscriptionContent.objects.get(id=int(request.POST["removeProduct"]))
        content.delete()
    returnValues['subscription_item'] = SubscriptionContent.objects.filter(subscription=subscription_id)
    returnValues['products'] = Product.objects.all()
    returnValues['products_json'] = json.dumps(list(Product.objects.all().values()))
    returnValues['subscription_size'] = int(subscription.size)
    return render(request, 'subscription_content.html',returnValues)
def is_subscription_content_valid(subscription,product,productAmount):
    currentProductContent = SubscriptionContent.objects.filter(subscription=subscription.id)
    maxSize = int(subscription.size)
    if not currentProductContent:
        currentAmount = 0
    else:
        currentAmount = 0
        for subContent in currentProductContent:
            currentAmount+=subContent.amount * subContent.product.units
    return maxSize<currentAmount+productAmount*product.units
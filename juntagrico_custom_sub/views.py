from django.contrib.auth.decorators import login_required

from django.shortcuts import render,get_object_or_404
from juntagrico_custom_sub.models import *
from juntagrico.models import *

import json
import logging

logger = logging.getLogger(__name__)

def subscription_content(request,subscription_id=None):
    returnValues = dict()
    member = request.user.member
    if subscription_id is None:
        subscription = member.subscription
    else:
        subscription = get_object_or_404(Subscription, id=subscription_id)
    subContent = SubscriptionContent.objects.get(subscription=subscription)
    products = Product.objects.all()
    if "saveContent" in request.POST:
        valid,error = new_content_valid(subscription,request,products)
        if valid:
            for product in products:
                subItem,p  = SubscriptionContentFutureItem.objects.get_or_create(product=product,subscription_content=subContent,defaults={'amount': 0,'product':product,'subscription_content':subContent})
                subItem.amount = request.POST.get("amount"+str(product.id),0)
                subItem.save()
        else:
            returnValues['error'] = error
    for prod in products:
        try:
            subItem = SubscriptionContentFutureItem.objects.get(subscription_content=subContent,product=prod.id)
            prod.amount_in_subscription = subItem.amount
        except SubscriptionContentFutureItem.DoesNotExist:
            prod.amount_in_subscription = 0
    returnValues['products'] = products
    returnValues['subscription_size'] = int(subscription.size)
    returnValues['future_subscription_size'] = int(calculate_future_size(subscription))
    return render(request, 'subscription_content.html',returnValues)

def new_content_valid(subscription,request,products):
    totalUnits = 0
    for product in products:
        productAmount = int(request.POST.get("amount"+str(product.id)))
        if(productAmount<0):
            return(False,"Mengen unter Null sind nicht erlaubt")
        totalUnits += productAmount * product.units
    if(totalUnits>int(calculate_future_size(subscription))):
        return(False,"Dein Abo hat nicht genug Platz für alle Produkte")
    return (True,"")

def calculate_future_size(subscription):
    result = 0
    for type in subscription.future_types.all():
        result += type.size.units
    return result
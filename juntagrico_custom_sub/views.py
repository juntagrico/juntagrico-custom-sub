import logging

from django.contrib.auth.decorators import permission_required
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from juntagrico import views_subscription
from juntagrico.entity.subtypes import SubscriptionType
from juntagrico.views import subscription as subscription_view
from juntagrico.mailer import adminnotification
from juntagrico.view_decorators import signup_session, primary_member_of_subscription, \
    primary_member_of_subscription_of_part
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.util import return_to_previous_location
from juntagrico.util.management_list import get_changedate

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent
from juntagrico_custom_sub.entity.subscription_content_future_item import SubscriptionContentFutureItem
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.entity.subscription_size_mandatory_products import SubscriptionBundleMandatoryProducts
from juntagrico_custom_sub.util.sub_content import new_content_valid

logger = logging.getLogger(__name__)


@primary_member_of_subscription
def cancel_part(request, part_id, subscription_id):
    """
    Overriden from core to redirect to the content change page
    """
    part = get_object_or_404(SubscriptionPart, subscription__id=subscription_id, id=part_id)
    part.cancel()
    adminnotification.subpart_canceled(part)
    return redirect("content_edit", subscription_id=subscription_id)


@primary_member_of_subscription_of_part
def part_change(request, part):
    """
    Overriden from core to redirect to the content change page
    """
    result = views_subscription.part_change(request, part_id=part.id)
    if isinstance(result, HttpResponseRedirect):
        return redirect("content_edit", subscription_id=part.subscription.id)
    return result


@primary_member_of_subscription
def part_order(request, subscription_id, extra=False):
    """
    Overriden from core to redirect to the content change page
    """
    result = subscription_view.part_order(request, subscription_id=subscription_id, extra=extra)
    if isinstance(result, HttpResponseRedirect):
        return redirect("content_edit", subscription_id=subscription_id)
    return result


@primary_member_of_subscription
def subscription_select_content(request, subscription_id):
    render_dict = dict()
    subscription = get_object_or_404(Subscription, id=subscription_id)
    subContent = SubscriptionContent.objects.get(subscription=subscription)

    fut_subs_types = count_subs_sizes(subscription.active_and_future_parts)

    total_units = sum(
        sub_type.bundle.product_sizes.aggregate(units=Sum('units'))['units'] * amount
        for sub_type, amount in fut_subs_types.items()
    )

    # products to be considered are only the ones that are editable or mandatory for the chosen sizes
    mand_products = SubscriptionBundleMandatoryProducts.objects.filter(
        subscription_bundle__types__in=fut_subs_types
    ).values_list("product_id", flat=True)

    products = Product.objects.filter(Q(user_editable=True) | Q(id__in=mand_products)).order_by("user_editable", "code")
    for prod in products:
        sub_item = SubscriptionContentFutureItem.objects.filter(subscription_content=subContent, product=prod).first()
        chosen_amount = 0 if not sub_item else sub_item.amount
        min_amount = determine_min_amount(prod, fut_subs_types)
        prod.min_amount = min(min_amount, chosen_amount)
        prod.amount_in_subscription = max(chosen_amount, min_amount)

    if "saveContent" in request.POST:
        custom_prods = parse_selected_custom_products(request.POST, products)
        error = new_content_valid(total_units, custom_prods, products)
        if not error:
            # if there were previous future items in the db, delete them
            SubscriptionContentFutureItem.objects.filter(subscription_content=subContent).delete()
            add_products_to_subscription(subscription_id, custom_prods, SubscriptionContentFutureItem)
            return redirect("content_edit_result", subscription_id=subscription_id)
        else:
            return redirect("content_edit", subscription_id=subscription_id)

    render_dict["subscription"] = subscription
    render_dict["products"] = products
    render_dict["future_subscription_size"] = total_units

    return render(request, "cs/subscription_select_content.html", render_dict)


@primary_member_of_subscription
def content_edit_result(request, subscription_id):
    return render(request, "cs/content_edit_result.html")


@signup_session
def initial_select_content(request, signup_manager):
    products = Product.objects.all().order_by("user_editable", "code")
    subs_types = {
        SubscriptionType.objects.get(id=subs_type): amount
        for subs_type, amount in signup_manager.get('subscriptions').items()
        if amount > 0
    }

    for p in products:
        p.min_amount = determine_min_amount(p, subs_types)
        p.amount_in_subscription = signup_manager.get('custom_products', {}).get(str(p.id), p.min_amount)

    total_units = sum(
        sub_type.bundle.product_sizes.aggregate(units=Sum('units'))['units'] * amount
        for sub_type, amount in subs_types.items()
    )

    error = None
    if request.method == "POST":
        # create dict with subscription type -> selected amount
        custom_prods = parse_selected_custom_products(request.POST, products)
        error = new_content_valid(total_units, custom_prods, products)
        if not error:
            signup_manager.set('custom_products', custom_prods)
            return redirect(signup_manager.get_next_page())

    return render(request, "cs/initial_select_content.html", {
        "products": products,
        "subscription_size": total_units,
        "future_subscription_size": total_units,
        "error": error,
    })


def add_products_to_subscription(subscription_id, custom_products, model):
    """
    adds custom products to the subscription with the given id.
    custom_prodducts is a dictionary with the product object as keys and their
    amount as value.
    model is either SubscriptionContentItem or SubscriptionContentFutureItem
    """
    content, created = SubscriptionContent.objects.get_or_create(subscription_id=subscription_id)
    for prod, amount in custom_products.items():
        item = model(amount=amount, product_id=prod, subscription_content_id=content.id)
        item.save()


def determine_min_amount(product, subs_types):
    """
    Given a product and a dictionary of subscription sizes, return the minimum (mandatory) amount.
    Allows for situations where a product can be mandatory for more than one size.
    Example of subs_sizes: {size_1: amount_1, size_2: amount_2, etc...}
    """
    return sum(
        product.subscriptionbundlemandatoryproducts_set.filter(subscription_bundle__types=sub_type).aggregate(
            required_amount=Sum('amount')
        ).get('required_amount') or 0 * amount
        for sub_type, amount in subs_types.items()
    )


def count_subs_sizes(subs_parts):
    rv = {}
    for st in subs_parts:
        if st.type not in rv:
            rv[st.type] = 1
        else:
            rv[st.type] += 1
    return rv


def parse_selected_custom_products(post_data, products):
    return {
        prod.id: int(post_data.get(f"amount{prod.id}", 0))
        for prod in products
        if int(post_data.get(f"amount{prod.id}")) > 0
    }


@permission_required("juntagrico.is_operations_group")
def list_content_changes(request, subscription_id=None):
    render_dict = get_changedate(request)
    changedlist = []
    subscriptions_list = Subscription.objects.active().filter(custom__isnull=False)
    for subscription in subscriptions_list:
        if subscription.custom.content_changed:
            changedlist.append(subscription)

    render_dict.update({
        'management_list': changedlist,
    })
    return render(request, "cs/list_content_changes.html", render_dict)


@permission_required("juntagrico.is_operations_group")
def activate_future_content(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    for content in subscription.custom.products.all():
        content.delete()
    for content in subscription.custom.future_products.all():
        SubscriptionContentItem.objects.create(
            subscription_content=subscription.custom, amount=content.amount, product=content.product
        )
    return return_to_previous_location(request)

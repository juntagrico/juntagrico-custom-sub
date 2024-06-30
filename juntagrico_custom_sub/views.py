import logging

from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from juntagrico import views_subscription
from juntagrico.views import subscription as subscription_view
from juntagrico.config import Config
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.mailer import adminnotification
from juntagrico.view_decorators import create_subscription_session, primary_member_of_subscription, \
    primary_member_of_subscription_of_part
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.util import return_to_previous_location, sessions
from juntagrico.util.management_list import get_changedate
from juntagrico.util.management import new_signup
from juntagrico.util.views_admin import subscription_management_list
from juntagrico.views_create_subscription import CSSummaryView

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent
from juntagrico_custom_sub.entity.subscription_content_future_item import SubscriptionContentFutureItem
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.entity.subscription_size_mandatory_products import SubscriptionSizeMandatoryProducts
from juntagrico_custom_sub.util.sub_content import calculate_future_size, new_content_valid

logger = logging.getLogger(__name__)

########################################################################################################################
# Monkey patching CSSessionObject
#
# Adds the custom product selectin to the signup process
########################################################################################################################
old_init = sessions.CSSessionObject.__init__
old_to_dict = sessions.CSSessionObject.to_dict


def new_init(self):
    old_init(self)
    self.custom_prod = {}
    self.error = None


def new_to_dict(self):
    result = old_to_dict(self)
    result["custom_prod"] = self.custom_prod
    return result


sessions.CSSessionObject.__init__ = new_init
sessions.CSSessionObject.to_dict = new_to_dict


def simple_get_size_name(types=None):
    types = types or []
    size_dict = []
    for type in types.all():
        size_dict.append(type.size.name + " " + type.size.product.name)
    if len(size_dict) > 0:
        return '<br>'.join(size_dict)
    return _('kein/e/n {0}').format(Config.vocabulary('subscription'))


Subscription.get_size_name = simple_get_size_name


def new_next_page(self):
    has_subs = self.subscription_size() > 0
    if not self.subscriptions:
        return "cs-subscription"
    elif has_subs and not self.custom_prod or new_content_valid(
            {subs: amount for subs, amount in self.subscriptions.items() if amount > 0}, self.custom_prod):
        self.custom_prod = {}
        return "custom_sub_initial_select"
    elif has_subs and not self.depot:
        return "cs-depot"
    elif has_subs and not self.start_date:
        return "cs-start"
    elif has_subs and not self.co_members_done:
        return "cs-co-members"
    elif not self.evaluate_ordered_shares():
        return "cs-shares"
    return "cs-summary"


sessions.CSSessionObject.next_page = new_next_page


###############################################################################
class CustomCSSummaryView(CSSummaryView):
    """
    Custom summary view for custom products.
    Overwrites post method to make sure custom products are added to the subscription
    """

    @transaction.atomic
    def form_valid(self, form):
        self.cs_session.main_member.comment = form.cleaned_data["comment"]
        # handle new signup
        registration_session = self.cs_session.pop()
        member = new_signup(registration_session)
        # associate custom products with subscription
        if member.subscription_future is not None:
            add_products_to_subscription(member.subscription_future.id, registration_session.custom_prod, SubscriptionContentItem)
            add_products_to_subscription(member.subscription_future.id, registration_session.custom_prod, SubscriptionContentFutureItem)
        # finish registration
        if member.subscription_future is None:
            return redirect('welcome')
        return redirect('welcome-with-sub')


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
    future_subscription_size = int(calculate_future_size(subscription))

    # products to be considered are only the ones that are editable or mandatory for the chosen sizes
    mand_products = SubscriptionSizeMandatoryProducts.objects.filter(
        subscription_size__in=[fst.size for fst in fut_subs_types.keys()]
    ).values_list("product_id", flat=True)
    products = Product.objects.filter(Q(user_editable=True) | Q(id__in=mand_products)).order_by("user_editable", "code")
    if "saveContent" in request.POST:
        custom_prods = parse_selected_custom_products(request.POST, products)
        error = new_content_valid(fut_subs_types, custom_prods, products)
        if not error:
            # if there were previous future items in the db, delete them
            SubscriptionContentFutureItem.objects.filter(subscription_content=subContent).delete()
            add_products_to_subscription(subscription_id, custom_prods, SubscriptionContentFutureItem)
            return redirect("content_edit_result", subscription_id=subscription_id)
        else:
            return redirect("content_edit", subscription_id=subscription_id)

    for prod in products:
        sub_item = SubscriptionContentFutureItem.objects.filter(subscription_content=subContent, product=prod).first()
        chosen_amount = 0 if not sub_item else sub_item.amount
        min_amount = determine_min_amount(prod, fut_subs_types)
        prod.min_amount = min(min_amount, chosen_amount)
        prod.amount_in_subscription = max(chosen_amount, min_amount)

    render_dict["subscription"] = subscription
    render_dict["products"] = products
    render_dict["future_subscription_size"] = future_subscription_size

    return render(request, "cs/subscription_select_content.html", render_dict)


@primary_member_of_subscription
def content_edit_result(request, subscription_id):
    return render(request, "cs/content_edit_result.html")


@create_subscription_session
def initial_select_content(request, cs_session):
    products = Product.objects.all().order_by("user_editable", "code")
    if request.method == "POST":
        # create dict with subscription type -> selected amount
        custom_prods = parse_selected_custom_products(request.POST, products)
        fut_subs_types = {subs: amount for subs, amount in cs_session.subscriptions.items() if amount > 0}
        error = new_content_valid(fut_subs_types, custom_prods, products)
        if not error:
            cs_session.custom_prod = custom_prods
            return redirect(cs_session.next_page())
        else:
            cs_session.error = error
            return redirect("custom_sub_initial_select")
    subs_types = {subs_type: amount for subs_type, amount in cs_session.subscriptions.items() if amount > 0}
    for p in products:
        p.min_amount = determine_min_amount(p, subs_types)
        if p in cs_session.custom_prod:
            p.amount_in_subscription = cs_session.custom_prod[p]
        else:
            p.amount_in_subscription = p.min_amount

    returnValues = {}
    returnValues["products"] = products
    returnValues["subscription_size"] = int(cs_session.subscription_size())
    returnValues["future_subscription_size"] = int(cs_session.subscription_size())
    returnValues = handle_error(returnValues, cs_session)
    return render(request, "cs/initial_select_content.html", returnValues)


def handle_error(render_dict, session_object):
    if session_object.error:
        render_dict["error"] = session_object.error
        session_object.error = None
    return render_dict


def add_products_to_subscription(subscription_id, custom_products, model):
    """
    adds custom products to the subscription with the given id.
    custom_prodducts is a dictionary with the product object as keys and their
    amount as value.
    model is either SubscriptionContentItem or SubscriptionContentFutureItem
    """
    content, created = SubscriptionContent.objects.get_or_create(subscription_id=subscription_id)
    for prod, amount in custom_products.items():
        item = model(amount=amount, product_id=prod.id, subscription_content_id=content.id)
        item.save()


def determine_min_amount(product, subs_types):
    """
    Given a product and a dictionary of subscription sizes, return the minimum (mandatory) amount.
    Allows for situations where a product can be mandatory for more than one size.
    Example of subs_sizes: {size_1: amount_1, size_2: amount_2, etc...}
    """
    min_amount = 0
    for st, count in subs_types.items():
        mand_prod = SubscriptionSizeMandatoryProducts.objects.filter(product=product, subscription_size=st.size).first()
        if mand_prod:
            min_amount += mand_prod.amount * count
    return min_amount


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
        prod: int(post_data.get(f"amount{prod.id}", 0))
        for prod in products
        if int(post_data.get(f"amount{prod.id}")) > 0
    }


@permission_required("juntagrico.is_operations_group")
def list_content_changes(request, subscription_id=None):
    render_dict = get_changedate(request)
    changedlist = []
    subscriptions_list = SubscriptionDao.all_active_subscritions()
    for subscription in subscriptions_list:
        if subscription.content.content_changed:
            changedlist.append(subscription)
    return subscription_management_list(changedlist, render_dict, "cs/list_content_changes.html", request)


@permission_required("juntagrico.is_operations_group")
def activate_future_content(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    for content in subscription.content.products.all():
        content.delete()
    for content in subscription.content.future_products.all():
        SubscriptionContentItem.objects.create(
            subscription_content=subscription.content, amount=content.amount, product=content.product
        )
    return return_to_previous_location(request)

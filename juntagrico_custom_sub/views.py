import logging

from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.forms import ValidationError

from juntagrico.config import Config
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.view_decorators import create_subscription_session, primary_member_of_subscription
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionType
from juntagrico.mailer import membernotification
from juntagrico.util import management as ja_mgmt
from juntagrico.util import return_to_previous_location, sessions, temporal
from juntagrico.util.management_list import get_changedate
from juntagrico.util.management import new_signup, create_subscription_parts
from juntagrico.util.views_admin import subscription_management_list
from juntagrico.views import get_menu_dict
from juntagrico.views import get_page_dict
from juntagrico.views_create_subscription import CSSummaryView

from juntagrico.forms import SubscriptionPartSelectForm, SubscriptionPartOrderForm

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


def simple_get_size_name(types=[]):
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
    elif has_subs and not self.custom_prod:
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


########################################################################################################################
class CustomCSSummaryView(CSSummaryView):
    """
    Custom summary view for custom products.
    Overwrites post method to make sure custom products are added to the subscription
    """

    template_name = "cs/initial_summary.html"

    @staticmethod
    def post(request, cs_session):
        # handle new signup
        registration_session = cs_session.pop()
        member = new_signup(registration_session)
        # associate custom products with subscription
        if member.subscription_future is not None:
            add_products_to_subscription(member.subscription_future.id, registration_session.custom_prod, SubscriptionContentItem)
            add_products_to_subscription(member.subscription_future.id, registration_session.custom_prod, SubscriptionContentFutureItem)
        # finish registration
        if member.subscription_future is None:
            return redirect('welcome')
        return redirect('welcome-with-sub')


@create_subscription_session
def initial_select_size(request, cs_session, **kwargs):
    if request.method == 'POST':
        form = SubscriptionPartSelectForm(cs_session.subscriptions, request.POST)
        if form.is_valid():
            selected = form.get_selected()
            cs_session.custom_prod = {}
            err_msg = quantity_error(selected)
            if not err_msg or request.POST.get("subscription") == "-1":
                cs_session.subscriptions = selected
                return redirect(cs_session.next_page())
            else:
                form.add_error(None,err_msg)
    else:
        form = SubscriptionPartSelectForm(cs_session.subscriptions)

    render_dict = get_page_dict(request)
    render_dict.update({
        'form': form,
        'subscription_selected': sum(form.get_selected().values()) > 0,
        'hours_used': Config.assignment_unit() == 'HOURS',
    })
    return render(request, 'cs/initial_select_size.html', render_dict)


@primary_member_of_subscription
@create_subscription_session
def size_change(request, cs_session, subscription_id):
    """
    Overriden from core
    change the size of a subscription
    """
    subscription = get_object_or_404(Subscription, id=subscription_id)
    parts_order_allowed = subscription.waiting or subscription.active
    if request.method == 'POST' and int(timezone.now().strftime("%m")) <= Config.business_year_cancelation_month():
        if not parts_order_allowed:
            raise ValidationError(_('Für gekündigte {} können keine Bestandteile bestellt werden').
                                  format(Config.vocabulary('subscription_pl')), code='invalid')
        form = SubscriptionPartOrderForm(subscription, request.POST)
        if form.is_valid():
            selected = form.get_selected()
            err_msg = quantity_error(selected,subscription.active_and_future_parts)
            if not err_msg:
                create_subscription_parts(subscription, selected)
                return redirect("content_edit", subscription_id=subscription_id)
            else:
                form.add_error(None,err_msg)  
    else:
        form = SubscriptionPartOrderForm()
    renderdict = get_menu_dict(request)
    renderdict.update({
        'form': form,
        'subscription': subscription,
        'hours_used': Config.assignment_unit() == 'HOURS',
        'next_cancel_date': temporal.next_cancelation_date(),
        'parts_order_allowed': parts_order_allowed,
    })
    return render(request, 'size_change.html', renderdict)

@primary_member_of_subscription
def cancel_part(request, part_id, subscription_id):
    """
    Overriden from core to redirect to the content change page
    """
    part = get_object_or_404(SubscriptionPart, subscription__id=subscription_id, id=part_id)
    if part.activation_date is None:
        part.delete()
    else:
        part.cancel()
    return redirect("content_edit", subscription_id=subscription_id)


def quantity_error(selected,active_parts=None):
    """
    validates the selected quantities for Basimilch's usecase
    selected is a dictionnary with SubscriptionType objects as keys and amounts as values
    """
    present4 = 0
    present8 = 0
    present2 = 0

    if active_parts:
        present4 = active_parts.filter(type__size__units=4).count()
        present8 = active_parts.filter(type__size__units=8).count()
        present2 = active_parts.filter(type__size__units=2).count()

    selected4 = selected[SubscriptionType.objects.get(size__units=4)]
    selected8 = selected[SubscriptionType.objects.get(size__units=8)]
    selected2 = selected[SubscriptionType.objects.get(size__units=2)]

    totalNew4 = present4 + selected4
    totalNew8 = present8 + selected8
    totalNew2 = present4 + selected4

    total_liters = totalNew4 * 4 + totalNew8 * 8 + totalNew2 * 2
    if total_liters < 4:
        return "Falls ein Abo gewünscht ist, müssen mindestens 4 Liter in einem Abo sein."
    required8 = total_liters // 8
    required4 = (total_liters % 8) // 4
    if not (totalNew8 == required8 and totalNew4 == required4):
        return "Du musst immer die grösstmögliche Abogrösse nehmen. \
            Es ist zum Beispiel nicht möglich, 8 Liter auf zwei Vierliter-Abos aufzuteilen."
    return ""


@primary_member_of_subscription
@create_subscription_session
def subscription_select_content(request, cs_session, subscription_id):
    render_dict = dict()
    subscription = get_object_or_404(Subscription, id=subscription_id)
    subContent = SubscriptionContent.objects.get(subscription=subscription)

    if cs_session.subscriptions:  # subscription size has been changed during previous step
        fut_subs_types = {subs_type: amount for subs_type, amount in cs_session.subscriptions.items() if amount > 0}
        future_subscription_size = cs_session.subscription_size()
    else:
        fut_subs_types = count_subs_sizes(subscription.future_parts)
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
            if cs_session.subscriptions:  # the user may get to this point without changing the subscription
                pass
                # TODO how does this need to be replaced
                #replace_subscription_types(subscription, cs_session.subscriptions)
            # if there were previous future items in the db, delete them
            SubscriptionContentFutureItem.objects.filter(subscription_content=subContent).delete()
            add_products_to_subscription(subscription_id, custom_prods, SubscriptionContentFutureItem)
            cs_session.clear()
            return redirect("content_edit_result", subscription_id=subscription_id)
        else:
            cs_session.error = error
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

    if cs_session.error:
        template = get_template("cs/snippets/error_message.html")
        render_result = template.render({"error": cs_session.error})
        render_dict["messages"] = [render_result]
        cs_session.error = None

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
            return redirect(reverse("custom_sub_initial_select"))
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
    render_dict = get_menu_dict(request)
    render_dict.update(get_changedate(request))
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

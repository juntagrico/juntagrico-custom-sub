import datetime
from io import StringIO

from django.contrib import admin
from django.core.management import call_command
from django.test import RequestFactory
from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInline
from juntagrico.entity.subs import Subscription
from juntagrico.forms import SubscriptionPartChangeForm, SubscriptionPartOrderForm, SubscriptionPartSelectForm

from juntagrico_custom_sub.defaults import depot_list_context, pack_list_context
from juntagrico_custom_sub.entity.cs_depot import CsDepot
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.util.interval import rhythm
from test import JuntagricoCustomSubTestCase


def is_even_week(date):
    # matches SubscriptionPartQuerySet.active_on for interval=2, offset=0
    return (date.isocalendar()[1] - 1) % 2 == 0


class RhythmTestCase(JuntagricoCustomSubTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        bundle = cls.sub_type.bundle
        cls.biweekly_type = cls.create_sub_type(bundle, shares=0, interval=2)
        cls.biweekly_type_shifted = cls.create_sub_type(bundle, shares=0, interval=2, offset=1)
        cls.weekly_type = cls.create_sub_type(bundle, shares=0)
        cls.weekly_extra_type = cls.create_sub_type(bundle, shares=0, is_extra=True)
        cls.member2 = cls.create_member('email2@email.org')
        cls.biweekly_sub = cls.create_subscription_with_parts(cls.member2, [cls.biweekly_type])
        today = datetime.date.today()
        # two consecutive weeks, exactly one of them is a biweekly delivery week (avoiding iso week 53)
        cls.monday = today - datetime.timedelta(today.weekday()) + datetime.timedelta(7)
        if cls.monday.isocalendar()[1] >= 52:
            cls.monday += datetime.timedelta(21)
        cls.on_week = cls.monday if is_even_week(cls.monday) else cls.monday + datetime.timedelta(7)
        cls.off_week = cls.on_week + datetime.timedelta(7)

    @classmethod
    def create_subscription_with_parts(cls, member, parts):
        sub = cls.create_sub_now(cls.depot1, parts)
        member.join_subscription(sub, True)
        return sub


class RhythmTest(RhythmTestCase):
    def test_rhythm_normalization(self):
        self.assertEqual(rhythm(self.weekly_type), rhythm(self.create_sub_type(self.sub_type.bundle, offset=3)))
        self.assertEqual(rhythm(self.biweekly_type), rhythm(self.create_sub_type(self.sub_type.bundle, interval=2, offset=2)))
        self.assertNotEqual(rhythm(self.biweekly_type), rhythm(self.biweekly_type_shifted))


class DepotListTest(RhythmTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        weekly_content = cls.create_subscription_content(cls.subscription1)
        SubscriptionContentItem.objects.create(subscription_content=weekly_content, product=cls.product1, amount=1)
        biweekly_content = cls.create_subscription_content(cls.biweekly_sub)
        SubscriptionContentItem.objects.create(subscription_content=biweekly_content, product=cls.product1, amount=3)
        cls.depot = CsDepot.objects.get(pk=cls.depot1.pk)

    def test_subscriptions_on(self):
        self.assertCountEqual(self.depot.subscriptions_on(self.on_week), [self.subscription1, self.biweekly_sub])
        self.assertCountEqual(self.depot.subscriptions_on(self.off_week), [self.subscription1])

    def test_product_totals_on(self):
        self.assertEqual(self.depot.product_totals_on(self.on_week)[self.product1], 4)
        self.assertEqual(self.depot.product_totals_on(self.off_week)[self.product1], 1)
        self.assertEqual(self.depot.product_totals_on(self.off_week)[self.product2], 0)

    def test_weekly_extra_does_not_make_subscription_weekly(self):
        self.biweekly_sub.parts.create(type=self.weekly_extra_type, activation_date=datetime.date.today())
        self.assertCountEqual(self.depot.subscriptions_on(self.off_week), [self.subscription1])

    def test_extra_only_subscription_is_not_listed(self):
        member = self.create_member('email3@email.org')
        extra_sub = self.create_subscription_with_parts(member, [self.weekly_extra_type])
        self.assertNotIn(extra_sub, self.depot.subscriptions_on(self.on_week))

    def test_mixed_rhythm_subscription_is_listed_if_any_part_is_due(self):
        self.biweekly_sub.parts.create(type=self.biweekly_type_shifted, activation_date=datetime.date.today())
        self.assertIn(self.biweekly_sub, self.depot.subscriptions_on(self.on_week))
        self.assertIn(self.biweekly_sub, self.depot.subscriptions_on(self.off_week))

    def test_list_contexts(self):
        depot = next(d for d in depot_list_context({'date': self.off_week})['depots'] if d.pk == self.depot.pk)
        self.assertCountEqual(depot.due_subscriptions, [self.subscription1])
        self.assertEqual(depot.due_product_totals[self.product1], 1)
        context = pack_list_context({'date': self.on_week})
        self.assertEqual(context['overallTotals'][0], 4)

    def test_generate_depot_list(self):
        for date in (self.on_week, self.off_week):
            days = (date - datetime.date.today()).days
            call_command('generate_depot_list', '--force', '--no-future', '--days', str(days), stdout=StringIO())


class ValidatorTest(RhythmTestCase):
    def assertRhythmError(self, form, expected=True):
        form.is_valid()
        codes = [e.code for e in form.non_field_errors().as_data()]
        self.assertEqual('inconsistent_rhythm' in codes, expected, form.errors)

    def test_signup_selection(self):
        self.assertRhythmError(SubscriptionPartSelectForm({}, {
            f'amount[{self.biweekly_type.pk}]': 1, f'amount[{self.weekly_type.pk}]': 1,
        }))
        self.assertRhythmError(SubscriptionPartSelectForm({}, {
            f'amount[{self.biweekly_type.pk}]': 2,
        }), expected=False)

    def test_order(self):
        self.assertRhythmError(SubscriptionPartOrderForm(self.biweekly_sub, {
            f'amount[{self.weekly_type.pk}]': 1,
        }))
        self.assertRhythmError(SubscriptionPartOrderForm(self.biweekly_sub, {
            f'amount[{self.biweekly_type.pk}]': 1,
        }), expected=False)

    def test_order_ignores_canceled_parts(self):
        self.biweekly_sub.parts.get().cancel()
        self.assertRhythmError(SubscriptionPartOrderForm(self.biweekly_sub, {
            f'amount[{self.weekly_type.pk}]': 1,
        }), expected=False)

    def test_change(self):
        self.biweekly_sub.parts.create(type=self.biweekly_type, activation_date=datetime.date.today())
        part = self.biweekly_sub.parts.first()
        self.assertRhythmError(SubscriptionPartChangeForm(part, {'part_type': self.weekly_type.pk}))
        self.assertRhythmError(SubscriptionPartChangeForm(part, {'part_type': self.biweekly_type_shifted.pk}))

    def test_change_of_only_part(self):
        part = self.biweekly_sub.parts.get()
        self.assertRhythmError(SubscriptionPartChangeForm(part, {'part_type': self.weekly_type.pk}), expected=False)

    def get_admin_formset(self, subscription, types):
        request = RequestFactory().post('/')
        request.user = self.admin.user
        inline = SubscriptionPartInline(Subscription, admin.site)
        formset_class = inline.get_formset(request, subscription)
        parts = list(subscription.parts.all())
        data = {
            'parts-TOTAL_FORMS': len(types), 'parts-INITIAL_FORMS': len(parts),
            'parts-MIN_NUM_FORMS': 0, 'parts-MAX_NUM_FORMS': 1000,
        }
        for i, sub_type in enumerate(types):
            data[f'parts-{i}-type'] = sub_type.pk
            data[f'parts-{i}-subscription'] = subscription.pk
            if i < len(parts):
                data[f'parts-{i}-id'] = parts[i].pk
                data[f'parts-{i}-activation_date'] = parts[i].activation_date
        return formset_class(data, instance=subscription, prefix='parts')

    def test_admin(self):
        formset = self.get_admin_formset(self.biweekly_sub, [self.biweekly_type, self.weekly_type])
        self.assertFalse(formset.is_valid())
        self.assertIn('inconsistent_rhythm', [e.code for e in formset.non_form_errors().as_data()])
        formset = self.get_admin_formset(self.biweekly_sub, [self.biweekly_type, self.biweekly_type])
        self.assertTrue(formset.is_valid(), formset.errors or formset.non_form_errors())

    def test_check_command(self):
        out = StringIO()
        call_command('cs_check_rhythms', stdout=out)
        self.assertEqual(out.getvalue(), '')
        self.biweekly_sub.parts.create(type=self.weekly_type)
        call_command('cs_check_rhythms', stdout=out)
        self.assertIn(f'{self.biweekly_sub.pk}:', out.getvalue())

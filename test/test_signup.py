from django.conf import settings
from django.core import mail
from django.urls import reverse
from juntagrico.config import Config
from juntagrico.entity.depot import Depot
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionType

from juntagrico_custom_sub.entity.product import Product
from test import JuntagricoCustomSubTestCase


class CustomSubTests(JuntagricoCustomSubTestCase):
    with_extra_subs = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_subscription_content(cls.subscription1)
        cls.create_product()
        cls.create_product(
            "2",
            name="Wochenkäse klein",
            units=2,
            unit_multiplier=100,
            unit_name="Gramm",
            user_editable=False
        )

    @staticmethod
    def newMemberData(email='test@user.com'):
        return {
            'last_name': 'Last Name',
            'first_name': 'First Name',
            'addr_street': 'Street',
            'addr_zipcode': '8000',
            'addr_location': 'Zurich',
            'phone': '044',
            'mobile_phone': '',
            'email': email,
            'birthday': '',
            'agb': 'on'
        }

    def assertGet(self, url, code=200, member=None, **kwargs):
        """ Stay logged out
        """
        response = self.client.get(url, **kwargs)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=302, member=None):
        """ Stay logged out
        """
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
        return response

    def signup(self, with_comment):
        new_member_data = self.newMemberData()
        if with_comment:
            new_member_data['comment'] = 'Short comment'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertRedirects(response, reverse('cs-subscription'))
        return new_member_data

    def commonAddSub(self, member_email, with_co_member, comment='', comment_in=0):
        initial_share_count = Share.objects.filter(member__email=member_email).count()
        self.addSubToSummary(with_co_member)
        response = self.client.post(reverse('cs-summary'), {'comment': comment})
        self.assertRedirects(response, reverse('welcome-with-sub'))
        self.assertEqual(Member.objects.filter(email=member_email).count(), 1)
        if settings.ENABLE_SHARES:
            self.assertEqual(Share.objects.filter(member__email=member_email).count(), initial_share_count + 1)
        subscription = Subscription.objects.filter(primary_member__email=member_email).first()
        self.assertNotEqual(subscription, None)
        # look for comment in admin notification
        self.assertIn(comment, mail.outbox[comment_in].body)
        self.assertEqual(subscription.primary_member.signup_comment, comment)

    def addSubToSummary(self, with_co_member=False):
        sub_types_id = SubscriptionType.objects.values_list('id', flat=True)
        response = self.client.post(
            reverse('cs-subscription'),
            {
                f'amount[{type_id}]': 1 if i == 0 else 0
                for i, type_id in enumerate(sub_types_id)
            }
        )
        if self.with_extra_subs:
            self.assertRedirects(response, reverse('cs-extras'))
            self.assertGet(reverse('cs-extras'))
            sub_types_id = SubscriptionType.objects.is_extra().values_list('id', flat=True)
            response = self.client.post(
                reverse('cs-extras'),
                {
                    f'amount[{type_id}]': 1 if i == 0 else 0
                    for i, type_id in enumerate(sub_types_id)
                }
            )
        # custom sub
        self.assertRedirects(response, reverse('custom_sub_initial_select'))
        self.assertGet(reverse('custom_sub_initial_select'))
        response = self.client.post(
            reverse('custom_sub_initial_select'),
            {
                f'amount{product.id}': 1 if product.id == 1 else 0
                for product in Product.objects.all()
            }
        )
        # continue normal signup
        self.assertRedirects(response, reverse('cs-depot'))
        self.assertGet(reverse('cs-depot'))
        depot_id = Depot.objects.values_list('id', flat=True)[0]
        response = self.client.post(
            reverse('cs-depot'),
            {
                'depot': depot_id,
            }
        )
        self.assertRedirects(response, reverse('cs-start'))
        self.assertGet(reverse('cs-start'))
        response = self.client.post(
            reverse('cs-start'),
            {
                'start_date': '01.01.2020',
                'initial-start_date': '2020-01-01'
            }
        )
        self.assertRedirects(response, reverse('cs-co-members'))
        self.assertGet(reverse('cs-co-members'))

        if with_co_member:
            co_member_data = self.newMemberData('test2@user.com')
            response = self.client.post(reverse('cs-co-members'), co_member_data)
            self.assertRedirects(response, reverse('cs-co-members'))
            self.assertGet(reverse('cs-co-members'))

        response = self.assertGet(reverse('cs-co-members'), 302, data={'next': '1'})
        if Config.enable_shares():
            self.assertRedirects(response, reverse('cs-shares'))
            self.assertGet(reverse('cs-shares'))
            response = self.client.post(
                reverse('cs-shares'),
                {
                    'of_member': 1,
                    'of_co_member[0]': 0,
                }
            )
        self.assertRedirects(response, reverse('cs-summary'))
        # confirm summary
        self.client.get(reverse('cs-summary'))

    def testSignup(self, with_co_member=False, with_comment=False):
        new_member_data = self.signup(with_comment)
        self.commonAddSub(new_member_data['email'], with_co_member, 'new test comment' if with_comment else '')
        mail_count = 0  # no admins created, thus no admin notifications
        if with_co_member:
            mail_count += 2  # Welcome to co-member & admin notification
        if settings.ENABLE_SHARES:
            mail_count += 2  # share email & admin notification
            # no shares are ordered for co-member, thus no more emails
        self.assertEqual(len(mail.outbox), mail_count)

        # signup with different case email address should return form error
        new_member_data['email'] = 'Test@user.com'
        response = self.client.post(reverse('signup'), new_member_data)
        self.assertEqual(response.status_code, 200)

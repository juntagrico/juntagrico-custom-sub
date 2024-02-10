import datetime
from functools import cached_property

from django.test import TestCase, override_settings
from django.core import mail

from juntagrico.entity.depot import Depot
from juntagrico.entity.location import Location
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JuntagricoCustomSubTestCase(TestCase):

    _count_sub_types = 0

    def setUp(self):
        mail.outbox.clear()

    @staticmethod
    def create_member(email):
        member_data = {'first_name': 'first_name',
                       'last_name': 'last_name',
                       'email': email,
                       'addr_street': 'addr_street',
                       'addr_zipcode': '1234',
                       'addr_location': 'addr_location',
                       'phone': 'phone',
                       'mobile_phone': 'phone',
                       'confirmed': True,
                       }
        member = Member.objects.create(**member_data)
        member.user.set_password('12345')
        member.user.save()
        return member

    @cached_property
    def member1(self):
        return self.create_member('email1@email.org')

    @staticmethod
    def create_location():
        location_data = {'name': 'Depot location',
                         'latitude': '12.513',
                         'longitude': '1.314',
                         'addr_street': 'Fakestreet 123',
                         'addr_zipcode': '1000',
                         'addr_location': 'Faketown',
                         'description': 'Place to be'}
        return Location.objects.create(**location_data)

    @cached_property
    def location1(self):
        return self.create_location()

    def create_depot(self):
        depot_data = {
            'name': 'depot',
            'contact': self.member1,
            'weekday': 1,
            'location': self.location1}
        return Depot.objects.create(**depot_data)

    @cached_property
    def depot1(self):
        return self.create_depot()

    @staticmethod
    def create_sub_type(size, shares=1, visible=True, required_assignments=10, required_core_assignments=3, price=1000, **kwargs):
        JuntagricoCustomSubTestCase._count_sub_types += 1
        name = kwargs.get('name', None)
        long_name = kwargs.get('long_name', 'sub_type_long_name')
        return SubscriptionType.objects.create(
            name=name or 'sub_type_name' + str(JuntagricoCustomSubTestCase._count_sub_types),
            long_name=long_name,
            size=size,
            shares=shares,
            visible=visible,
            required_assignments=required_assignments,
            required_core_assignments=required_core_assignments,
            price=price,
            **kwargs
        )

    @cached_property
    def subscription_type1(self):
        """
        subscription product, size and types
        """
        sub_product_data = {
            'name': 'product'
        }
        sub_product = SubscriptionProduct.objects.create(**sub_product_data)
        sub_size_data = {
            'name': 'sub_name',
            'long_name': 'sub_long_name',
            'units': 1,
            'visible': True,
            'depot_list': True,
            'product': sub_product,
            'description': 'sub_desc'
        }
        sub_size = SubscriptionSize.objects.create(**sub_size_data)
        return self.create_sub_type(sub_size)

    @staticmethod
    def create_sub(depot, activation_date=None, parts=None, **kwargs):
        if 'deactivation_date' in kwargs and 'cancellation_date' not in kwargs:
            kwargs['cancellation_date'] = activation_date
        sub = Subscription.objects.create(
            depot=depot,
            activation_date=activation_date,
            creation_date='2017-03-27',
            start_date='2018-01-01',
            **kwargs
        )
        if parts:
            for part in parts:
                SubscriptionPart.objects.create(
                    subscription=sub,
                    type=part,
                    activation_date=activation_date,
                    cancellation_date=kwargs.get('cancellation_date', None),
                    deactivation_date=kwargs.get('deactivation_date', None)
                )
        return sub

    @classmethod
    def create_sub_now(cls, depot, **kwargs):
        return cls.create_sub(depot, datetime.date.today(), **kwargs)

    @cached_property
    def subscription1(self):
        """
        subscription
        """
        sub = self.create_sub_now(self.depot1)
        self.member1.join_subscription(sub, True)
        SubscriptionPart.objects.create(subscription=sub, type=self.subscription_type1,
                                        activation_date=datetime.date.today())
        return sub

    @staticmethod
    def create_subscription_content(subscription):
        return SubscriptionContent.objects.create(subscription=subscription)

    @staticmethod
    def create_product(code="1", name="Rohmilch", units=1, unit_name="Liter", **kwargs):
        return Product.objects.create(code=code, name=name, units=units, unit_name=unit_name, **kwargs)

    def assertGet(self, url, code=200, member=None):
        login_member = member or self.member1
        self.client.force_login(login_member.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, code)
        return response

    def assertPost(self, url, data=None, code=200, member=None):
        login_member = member or self.member1
        self.client.force_login(login_member.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, code)
        return response

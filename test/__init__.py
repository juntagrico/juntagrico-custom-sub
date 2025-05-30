import datetime

from django.test import TestCase, override_settings
from django.core import mail

from juntagrico.entity.depot import Depot
from juntagrico.entity.location import Location
from juntagrico.entity.member import Member
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType

from juntagrico_custom_sub.entity.custom_delivery import CustomDelivery, CustomDeliveryProduct
from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class JuntagricoCustomSubTestCase(TestCase):

    _count_sub_types = 0

    @classmethod
    def setUpTestData(cls):
        cls.member1 = cls.create_member('email1@email.org')
        cls.admin = cls.create_member('admin@example.com')
        cls.admin.user.is_superuser = True
        cls.admin.user.is_staff = True
        cls.admin.user.save()
        cls.location1 = cls.create_location()
        cls.depot1 = cls.create_depot(cls.member1, cls.location1)
        cls.subscription_type1 = cls.create_subscription_type1()
        cls.subscription1 = cls.create_subscription_with_member(cls.member1, cls.depot1, cls.subscription_type1)
        cls.product1 = cls.create_product("code1", "Product1", )
        cls.product2 = cls.create_product("code2", "Product2", 2, "pieces")
        cls.custom_delivery = cls.create_custom_delivery([cls.product1, cls.product2])
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

    @staticmethod
    def create_depot(contact, location):
        depot_data = {
            'name': 'depot',
            'contact': contact,
            'weekday': 1,
            'location': location
        }
        return Depot.objects.create(**depot_data)

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

    @classmethod
    def create_subscription_type1(cls):
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
        return cls.create_sub_type(sub_size)

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

    @classmethod
    def create_subscription_with_member(cls, member, depot, subscription_type):
        """
        subscription
        """
        sub = cls.create_sub_now(depot)
        member.join_subscription(sub, True)
        SubscriptionPart.objects.create(subscription=sub, type=subscription_type,
                                        activation_date=datetime.date.today())
        return sub

    @staticmethod
    def create_subscription_content(subscription):
        return SubscriptionContent.objects.create(subscription=subscription)

    @staticmethod
    def create_product(code="1", name="Rohmilch", units=1, unit_name="Liter", **kwargs):
        return Product.objects.create(code=code, name=name, units=units, unit_name=unit_name, **kwargs)

    @staticmethod
    def create_custom_delivery(products):
        delivery = CustomDelivery.objects.create(delivery_date=datetime.date.today(), delivery_comment='test comment')
        for product in products:
            CustomDeliveryProduct.objects.create(delivery=delivery, product=product, name=str(product) + ' name')
        return delivery

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

import datetime

from django.core import mail

from juntagrico.tests import JuntagricoTestCase

from juntagrico.entity.depot import Depot
from juntagrico.entity.subtypes import SubscriptionProduct, ProductSize, SubscriptionCategory, \
    SubscriptionBundleProductSize

from juntagrico_custom_sub.entity.custom_delivery import CustomDelivery, CustomDeliveryProduct
from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent


class JuntagricoCustomSubTestCase(JuntagricoTestCase):
    fixtures = []
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
        cls.sub_type = cls.subscription_type1 = cls.create_subscription_type1()
        cls.subscription1 = cls.create_subscription_with_member(cls.member1, cls.depot1, cls.subscription_type1)
        cls.product1 = cls.create_product("code1", "Product1", )
        cls.product2 = cls.create_product("code2", "Product2", 2, "pieces")
        cls.custom_delivery = cls.create_custom_delivery([cls.product1, cls.product2])
        mail.outbox.clear()

    @staticmethod
    def create_depot(contact, location):
        depot_data = {
            'name': 'depot',
            'weekday': 1,
            'location': location
        }
        return Depot.objects.create(**depot_data)

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
            'units': 1,
            'show_on_depot_list': True,
            'product': sub_product,
        }
        sub_size = ProductSize.objects.create(**sub_size_data)
        sub_category = SubscriptionCategory.objects.create(name='sub_category')
        sub_bundle = cls.create_bundle('bundle1', sub_category, description='bundle description')
        SubscriptionBundleProductSize.objects.create(bundle=sub_bundle, product_size=sub_size)
        return cls.create_sub_type(sub_bundle)

    @classmethod
    def create_subscription_with_member(cls, member, depot, subscription_type):
        """
        subscription
        """
        sub = cls.create_sub_now(depot)
        member.join_subscription(sub, True)
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

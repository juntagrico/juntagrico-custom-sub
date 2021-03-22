from django.urls import reverse
from test.util.test import JuntagricoTestCase

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent


class JuntagricoCustomSubTestCase(JuntagricoTestCase):
    def setUp(self):
        super(JuntagricoCustomSubTestCase, self).setUp()
        self.set_up_products()
        self.set_up_sub_content()

    def set_up_sub_content(self):
        sub_content_data = {'subscription': self.sub}
        sub_content_data2 = {'subscription': self.sub2}
        subContent1 = SubscriptionContent.objects.create(**sub_content_data)
        subContent2 = SubscriptionContent.objects.create(**sub_content_data2)

        self.sub.content = subContent1
        self.sub2.content = subContent2

    def set_up_products(self):
        prod1_fields = {
            "name": "Rohmilch",
            "units": 1,
            "unit_multiplier": 1,
            "unit_name": "Liter",
        }
        prod2_fields = {
            "name": "Wochenkäse klein",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
        }
        self.product1 = Product.objects.create(**prod1_fields)
        self.product2 = Product.objects.create(**prod2_fields)


class CustomSubTests(JuntagricoCustomSubTestCase):
    def testSub(self):
        self.assertGet(reverse('sub-detail'))
        self.assertGet(reverse('sub-detail-id', args=[self.sub.pk]))

    def testContentChange(self):
        self.assertGet(reverse('content_edit', args=[self.sub.pk]))
        self.assertPost(reverse('content_edit', args=[self.sub.pk]),
                        {'saveContent': True, 'amount1': '1', 'amount2': '1'}, code=302)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.content.future_products.get(id=1).amount, 1)

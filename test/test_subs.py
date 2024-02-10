from django.urls import reverse

from test import JuntagricoCustomSubTestCase


class CustomSubTests(JuntagricoCustomSubTestCase):
    def setUp(self):
        super().setUp()
        self.create_subscription_content(self.subscription1)
        self.create_product()
        self.create_product(
            "2",
            name="Wochenkäse klein",
            units=2,
            unit_multiplier=100,
            unit_name="Gramm",
            user_editable=False
        )

    def testSub(self):
        self.assertGet(reverse('sub-detail'))
        self.assertGet(reverse('sub-detail-id', args=[self.subscription1.pk]))

    def testContentChange(self):
        self.assertGet(reverse('content_edit', args=[self.subscription1.pk]))
        self.assertPost(reverse('content_edit', args=[self.subscription1.pk]),
                        {'saveContent': True, 'amount1': '1', 'amount2': '1'}, code=302)
        self.subscription1.refresh_from_db()
        self.assertEqual(self.subscription1.content.future_products.get(id=1).amount, 1)

from django.db.models import Count
from django.test import override_settings
from django.urls import reverse

from test import JuntagricoCustomSubTestCase


class CustomSubTests(JuntagricoCustomSubTestCase):
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

    @override_settings(ROOT_URLCONF='testurls_downgraded')
    def testOldSub(self):
        self.assertGet(reverse('subscription-landing'))
        self.assertGet(reverse('subscription-single', args=[self.subscription1.pk]))

    def testSub(self):
        self.assertGet(reverse('subscription-landing'), code=302)
        self.assertGet(reverse('subscription-single', args=[self.subscription1.pk]))

    def testContentChange(self):
        self.assertGet(reverse('content_edit', args=[self.subscription1.pk]))
        self.assertPost(reverse('content_edit', args=[self.subscription1.pk]), {
            'saveContent': True, 'amount1': '0', 'amount2': '0', 'amount3': '1', 'amount4': '1'
        }, code=302)
        self.subscription1.refresh_from_db()
        self.assertEqual(self.subscription1.custom.future_products.aggregate(Count('amount'))['amount__count'], 1)

    def testChangeList(self):
        self.assertGet(reverse('content_change_list'), code=302)
        self.assertGet(reverse('content_change_list'), member=self.admin)

    def testCancelPartRedirectsToContentEdit(self):
        part = self.subscription1.parts.first()
        url = reverse('part-cancel', args=[part.id])
        # core templates reverse 'part-cancel' with the part id only. It must resolve to the plugin view
        self.assertEqual(url, f'/my/subscription/part/{part.id}/cancel')
        response = self.assertGet(url, code=302)
        self.assertRedirects(response, reverse('content_edit', args=[self.subscription1.pk]))
        part.refresh_from_db()
        self.assertIsNotNone(part.cancellation_date)

    def _set_changed_content(self):
        content = self.subscription1.custom
        content.products.create(product=self.product1, amount=1)
        content.future_products.create(product=self.product1, amount=2)
        content.future_products.create(product=self.product2, amount=1)
        return content

    def testChangeListShowsChangedContent(self):
        self._set_changed_content()
        response = self.assertGet(reverse('content_change_list'), member=self.admin)
        self.assertEqual(response.context['management_list'], [self.subscription1])
        self.assertContains(response, reverse('content_activate', args=[self.subscription1.pk]))

    def testActivateFutureContent(self):
        content = self._set_changed_content()
        url = reverse('content_activate', args=[self.subscription1.pk])
        # must not change data on GET
        self.assertGet(url, code=405, member=self.admin)
        self.assertTrue(content.content_changed)
        self.assertPost(url, code=302, member=self.admin)
        self.assertFalse(content.content_changed)
        self.assertEqual(
            dict(content.products.values_list('product_id', 'amount')),
            {self.product1.id: 2, self.product2.id: 1},
        )

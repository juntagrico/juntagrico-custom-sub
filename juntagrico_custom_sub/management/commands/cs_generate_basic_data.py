# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from juntagrico import entity as jm
from django.db import transaction

from juntagrico_custom_sub import entity as csm


def create_bundle(category, product_size, size=4, bundle_name=None):
    bundle_fields = {
        'long_name': bundle_name or f'{size} Liter',
        'category': category,
        'description': f'{size} Liter Abo enthält Produkte die {size} Liter Milch entsprechen.'
    }
    bundle = jm.subtypes.SubscriptionBundle.objects.filter(
        long_name=bundle_name, category=bundle_fields['category']
    ).first()
    if not bundle:
        bundle = jm.subtypes.SubscriptionBundle.objects.create(**bundle_fields)
    if product_size not in bundle.product_sizes.all():
        jm.subtypes.SubscriptionBundleProductSize.objects.create(bundle=bundle, product_size=product_size)
    return bundle


class Command(BaseCommand):

    # entry point used by manage.py
    @transaction.atomic
    def handle(self, *args, **options):
        subprod_fields = {"name": "Milch"}
        subproduct = jm.subtypes.SubscriptionProduct.objects.create(**subprod_fields)
        subsize1_fields = {
            "name": "4 Liter",
            "units": 4,
            "product": subproduct,
        }
        subsize3_fields = {
            "name": "8 Liter",
            "units": 8,
            "product": subproduct,
        }
        subsize4_fields = {
            "name": "2 Liter",
            "units": 2,
            "product": subproduct,
        }
        subsize1 = jm.subtypes.ProductSize.objects.create(**subsize1_fields)
        subsize3 = jm.subtypes.ProductSize.objects.create(**subsize3_fields)
        subsize4 = jm.subtypes.ProductSize.objects.create(**subsize4_fields)

        category, _ = jm.subtypes.SubscriptionCategory.objects.get_or_create(
            name='Kategorie 1', description='Beschreibung 1'
        )
        bundle1 = create_bundle(category, subsize1, 4)
        bundle3 = create_bundle(category, subsize3, 8)
        bundle4 = create_bundle(category, subsize4, 2)

        subtype1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "bundle": bundle1,
            "shares": 1,
            "visible": True,
            "required_assignments": 2,
            "price": 650,
            "description": "4-Liter-Abo.",
        }
        subtype3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter",
            "bundle": bundle3,
            "shares": 2,
            "visible": True,
            "required_assignments": 4,
            "price": 1200,
            "description": "8-Liter-Abo.",
        }
        subtype4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter",
            "bundle": bundle4,
            "shares": 0,
            "visible": True,
            "required_assignments": 1,
            "price": 300,
            "description": "2-Liter-Abo.",
        }
        jm.subtypes.SubscriptionType.objects.create(**subtype1_fields)
        jm.subtypes.SubscriptionType.objects.create(**subtype3_fields)
        jm.subtypes.SubscriptionType.objects.create(**subtype4_fields)

        # CS specific
        prod1_fields = {
            "name": "Rohmilch",
            "units": 1,
            "unit_multiplier": 1,
            "unit_name": "Liter",
            "code": "1",
        }
        prod2_fields = {
            "name": "Zusatzkäse",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "code": "2",
        }
        prod3_fields = {
            "name": "Quark",
            "units": 1,
            "unit_multiplier": 350,
            "unit_name": "Gramm",
            "code": "3",
        }
        prod4_fields = {
            "name": "Fruchtjoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
            "code": "4",
        }
        prod5_fields = {
            "name": "Naturejoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
            "code": "5",
        }
        prod6_fields = {
            "name": "Wochenkäse klein",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
            "code": "6",
        }
        prod7_fields = {
            "name": "Wochenkäse gross",
            "units": 4,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
            "code": "7",
        }
        csm.product.Product.objects.create(**prod1_fields)
        csm.product.Product.objects.create(**prod2_fields)
        csm.product.Product.objects.create(**prod3_fields)
        csm.product.Product.objects.create(**prod4_fields)
        csm.product.Product.objects.create(**prod5_fields)
        wochenkase_klein = csm.product.Product.objects.create(**prod6_fields)
        wochenkase_gross = csm.product.Product.objects.create(**prod7_fields)

        mandatory1_fields = {
            "subscription_bundle": bundle1,
            "product": wochenkase_klein,
            "amount": 1,
        }
        mandatory3_fields = {
            "subscription_bundle": bundle3,
            "product": wochenkase_gross,
            "amount": 1,
        }
        csm.subscription_size_mandatory_products.SubscriptionBundleMandatoryProducts.objects.create(**mandatory1_fields)
        csm.subscription_size_mandatory_products.SubscriptionBundleMandatoryProducts.objects.create(**mandatory3_fields)

# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from juntagrico import entity as jm
from django.db import transaction

from juntagrico_custom_sub import entity as csm


class Command(BaseCommand):

    # entry point used by manage.py
    @transaction.atomic
    def handle(self, *args, **options):
        subprod_fields = {"name": "Milch"}
        subproduct = jm.subtypes.SubscriptionProduct.objects.create(**subprod_fields)
        subsize1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "units": 4,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "Enthält Produkte, die 4 Liter Milch entsprechen.",
        }
        subsize3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter Abo",
            "units": 8,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "Enthält Produkte, die 8 Litern Milch entsprechen.",
        }
        subsize4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter Abo",
            "units": 2,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "Enthält Produkte, die 2 Litern Milch entsprechen.",
        }
        subsize1 = jm.subtypes.SubscriptionSize.objects.create(**subsize1_fields)
        subsize3 = jm.subtypes.SubscriptionSize.objects.create(**subsize3_fields)
        subsize4 = jm.subtypes.SubscriptionSize.objects.create(**subsize4_fields)
        subtrype1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "size": subsize1,
            "shares": 1,
            "visible": True,
            "required_assignments": 2,
            "price": 650,
            "description": "4-Liter-Abo.",
        }
        subtrype3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter",
            "size": subsize3,
            "shares": 2,
            "visible": True,
            "required_assignments": 4,
            "price": 1200,
            "description": "8-Liter-Abo.",
        }
        subtrype4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter",
            "size": subsize4,
            "shares": 0,
            "visible": True,
            "required_assignments": 1,
            "price": 300,
            "description": "2-Liter-Abo.",
        }
        jm.subtypes.SubscriptionType.objects.create(**subtrype1_fields)
        jm.subtypes.SubscriptionType.objects.create(**subtrype3_fields)
        jm.subtypes.SubscriptionType.objects.create(**subtrype4_fields)

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
            "subscription_size": subsize1,
            "product": wochenkase_klein,
            "amount": 1,
        }
        mandatory3_fields = {
            "subscription_size": subsize3,
            "product": wochenkase_gross,
            "amount": 1,
        }
        csm.subscription_size_mandatory_products.SubscriptionSizeMandatoryProducts.objects.create(**mandatory1_fields)
        csm.subscription_size_mandatory_products.SubscriptionSizeMandatoryProducts.objects.create(**mandatory3_fields)

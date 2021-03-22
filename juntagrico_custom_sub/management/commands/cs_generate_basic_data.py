# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from juntagrico import models as jm

from juntagrico_custom_sub import models as csm


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        subprod_fields = {"name": "Milch"}
        subproduct = jm.SubscriptionProduct.objects.create(**subprod_fields)
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
        subsize1 = jm.SubscriptionSize.objects.create(**subsize1_fields)
        subsize3 = jm.SubscriptionSize.objects.create(**subsize3_fields)
        subsize4 = jm.SubscriptionSize.objects.create(**subsize4_fields)
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
        jm.SubscriptionType.objects.create(**subtrype1_fields)
        jm.SubscriptionType.objects.create(**subtrype3_fields)
        jm.SubscriptionType.objects.create(**subtrype4_fields)

        # CS specific
        prod1_fields = {
            "name": "Rohmilch",
            "units": 1,
            "unit_multiplier": 1,
            "unit_name": "Liter",
        }
        prod2_fields = {
            "name": "Zusatzkäse",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
        }
        prod3_fields = {
            "name": "Quark",
            "units": 1,
            "unit_multiplier": 350,
            "unit_name": "Gramm",
        }
        prod4_fields = {
            "name": "Fruchtjoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
        }
        prod5_fields = {
            "name": "Naturejoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
        }
        prod6_fields = {
            "name": "Wochenkäse klein",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
        }
        prod7_fields = {
            "name": "Wochenkäse gross",
            "units": 4,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
        }
        csm.Product.objects.create(**prod1_fields)
        csm.Product.objects.create(**prod2_fields)
        csm.Product.objects.create(**prod3_fields)
        csm.Product.objects.create(**prod4_fields)
        csm.Product.objects.create(**prod5_fields)
        wochenkase_klein = csm.Product.objects.create(**prod6_fields)
        wochenkase_gross = csm.Product.objects.create(**prod7_fields)

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
        csm.SubscriptionSizeMandatoryProducts.objects.create(**mandatory1_fields)
        csm.SubscriptionSizeMandatoryProducts.objects.create(**mandatory3_fields)

        # add extra subscriptions (Zusatzabos)
        extra_sub_cat1 = jm.ExtraSubscriptionCategory.objects.create(
            name="Spezialkäse",
            description="Spezialkäse für Waghalsige Käseliebhaber",
            sort_order=1,
            visible=True,
        )
        extra_sub_type1 = jm.ExtraSubscriptionType.objects.create(
            name="Spezialkäse Einheitsgrösse",
            size="Einheitsgrösse",
            description="Einmal pro Monat Überraschunskäse",
            sort_order=1,
            category_id=extra_sub_cat1.id,
            visible=True,
        )
        jm.ExtraSubBillingPeriod.objects.create(
            start_day=1,
            start_month=1,
            end_day=31,
            end_month=12,
            type_id=extra_sub_type1.id,
            cancel_day=30,
            cancel_month=9,
            price=120,
        )

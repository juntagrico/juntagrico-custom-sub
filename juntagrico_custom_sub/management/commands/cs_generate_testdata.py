# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand
from juntagrico.entity.billing import BillingPeriod
from juntagrico.entity.depot import Depot
from juntagrico.entity.location import Location

from juntagrico.entity.member import Member
from juntagrico.entity.subs import SubscriptionPart, Subscription
from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionType, SubscriptionSize

from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent
from juntagrico_custom_sub.entity.subscription_content_future_item import SubscriptionContentFutureItem
from juntagrico_custom_sub.entity.subscription_content_item import SubscriptionContentItem
from juntagrico_custom_sub.entity.subscription_size_mandatory_products import SubscriptionSizeMandatoryProducts


class Command(BaseCommand):

    @staticmethod
    def create_subscription(depot, member, subtype, activation_date=None, ):
        sub_fields = {'depot': depot, 'future_depot': None,
                      'activation_date': activation_date,
                      'deactivation_date': None, 'creation_date': '2017-03-27', 'start_date': '2018-01-01'}
        subscription = Subscription.objects.create(**sub_fields)
        if member.subscription_current:
            member.subscription_current.delete()
        member.join_subscription(subscription)
        subscription.primary_member = member
        subscription.save()
        SubscriptionPart.objects.create(subscription=subscription, type=subtype,
                                        activation_date=activation_date)
        return subscription

    # entry point used by manage.py
    def handle(self, *args, **options):
        subproduct, _ = SubscriptionProduct.objects.get_or_create(name="Milch")
        subsize1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "units": 4,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "4 Liter Abo enthält Produkte die 4 Liter Milch entsprechen.",
        }
        subsize3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter Abo",
            "units": 8,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "8 Liter Abo enthält Produkte die 8 Liter Milch entsprechen.",
        }
        subsize4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter Abo",
            "units": 2,
            "visible": True,
            "depot_list": True,
            "product": subproduct,
            "description": "2 Liter Abo enthält Produkte die 2 Liter Milch entsprechen.",
        }
        subsize1, _ = SubscriptionSize.objects.get_or_create(name=subsize1_fields['name'], defaults=subsize1_fields)
        subsize3, _ = SubscriptionSize.objects.get_or_create(name=subsize3_fields['name'], defaults=subsize3_fields)
        subsize4, _ = SubscriptionSize.objects.get_or_create(name=subsize4_fields['name'], defaults=subsize4_fields)
        subtype1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "size": subsize1,
            "shares": 1,
            "visible": True,
            "required_assignments": 2,
            "price": 650,
            "description": "4 Liter Abo.",
        }
        subtype3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter",
            "size": subsize3,
            "shares": 2,
            "visible": True,
            "required_assignments": 4,
            "price": 1200,
            "description": "8 Liter Abo.",
        }
        subtype4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter",
            "size": subsize4,
            "shares": 0,
            "visible": True,
            "required_assignments": 1,
            "price": 300,
            "description": "2 Liter Abo.",
        }
        subtype1, _ = SubscriptionType.objects.get_or_create(name=subtype1_fields['name'], defaults=subtype1_fields)
        subtype3, _ = SubscriptionType.objects.get_or_create(name=subtype3_fields['name'], defaults=subtype3_fields)
        SubscriptionType.objects.get_or_create(name=subtype4_fields['name'], defaults=subtype4_fields)

        mem1_fields = {'first_name': 'Hans', 'last_name': 'Meyer', 'email': 'hand.meyer@juntagrico.juntagrico',
                       'addr_street': 'Sonnenbergstr 57', 'addr_zipcode': '2904', 'addr_location': 'Bressaucourt',
                       'birthday': '1947-03-27', 'phone': '032 738 64 73', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False}
        mem2_fields = {'first_name': 'Gertrud', 'last_name': 'Müller',
                       'email': 'gertrud.mueller@juntagico.juntagrico', 'addr_street': 'Im Wingert 9',
                       'addr_zipcode': '8584', 'addr_location': 'Leimbach', 'birthday': '1955-12-27',
                       'phone': '052 423 72 32', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False}
        member_1, _ = Member.objects.get_or_create(email=mem1_fields['email'], defaults=mem1_fields)
        member_2, _ = Member.objects.get_or_create(email=mem2_fields['email'], defaults=mem2_fields)

        depot1_location_fields = {'name': 'Depot Toblerplatz', 'latitude': '47.379308',
                                  'longitude': '8.559405', 'addr_street': 'Toblerstrasse 73', 'addr_zipcode': '8044',
                                  'addr_location': 'Zürich'}
        depot1_location, _ = Location.objects.get_or_create(name=depot1_location_fields['name'],
                                                            defaults=depot1_location_fields)
        depot1_fields = {'name': 'Toblerplatz', 'weekday': 2, 'location': depot1_location,
                         'description': 'Hinter dem Migros', 'contact': member_2}
        depot1, _ = Depot.objects.get_or_create(name=depot1_fields['name'], defaults=depot1_fields)

        activation_date = datetime.datetime.strptime('27/03/17', '%d/%m/%y').date()
        subscription_1 = self.create_subscription(depot1, member_1, subtype1, activation_date)
        subscription_2 = self.create_subscription(depot1, member_2, subtype3, activation_date)

        # CS specific
        prod1_fields = {
            "name": "Rohmilch",
            "units": 1,
            "unit_multiplier": 1,
            "unit_name": "Liter",
            "code": "A1",
        }
        prod2_fields = {
            "name": "Zusatzkäse",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "code": "A2"
        }
        prod3_fields = {
            "name": "Quark",
            "units": 1,
            "unit_multiplier": 350,
            "unit_name": "Gramm",
            "code": "A3"
        }
        prod4_fields = {
            "name": "Fruchtjoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
            "code": "A4"
        }
        prod5_fields = {
            "name": "Naturejoghurt",
            "units": 0.5,
            "unit_multiplier": 1000,
            "unit_name": "Gramm",
            "code": "A5"
        }
        prod6_fields = {
            "name": "Wochenkäse klein",
            "units": 2,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
            "code": "A6"
        }
        prod7_fields = {
            "name": "Wochenkäse gross",
            "units": 4,
            "unit_multiplier": 100,
            "unit_name": "Gramm",
            "user_editable": False,
            "code": "A7"
        }
        Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod1_fields)
        Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod2_fields)
        Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod3_fields)
        Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod4_fields)
        Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod5_fields)
        wochenkase_klein, _ = Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod6_fields)
        wochenkase_gross, _ = Product.objects.get_or_create(code=prod1_fields['code'], defaults=prod7_fields)

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
        SubscriptionSizeMandatoryProducts.objects.get_or_create(**mandatory1_fields)
        SubscriptionSizeMandatoryProducts.objects.get_or_create(**mandatory3_fields)

        subcontent1_fields = {"subscription": subscription_1}
        subcontent2_fields = {"subscription": subscription_2}
        subcontent1 = SubscriptionContent.objects.create(**subcontent1_fields)
        subcontent2 = SubscriptionContent.objects.create(**subcontent2_fields)

        subcontentitem1_fields = {
            "subscription_content": subcontent1,
            "product": wochenkase_klein,
        }
        subcontentitem2_fields = {
            "subscription_content": subcontent2,
            "product": wochenkase_gross,
        }
        defaults = {"amount": 1}
        SubscriptionContentItem.objects.get_or_create(**subcontentitem1_fields, defaults=defaults)
        SubscriptionContentItem.objects.get_or_create(**subcontentitem2_fields, defaults=defaults)

        SubscriptionContentFutureItem.objects.get_or_create(**subcontentitem1_fields, defaults=defaults)
        SubscriptionContentFutureItem.objects.get_or_create(**subcontentitem2_fields, defaults=defaults)

        # add extra subscriptions (Zusatzabos)
        extra_sub_product, _ = SubscriptionProduct.objects.get_or_create(
            name="Spezialkäse",
            defaults=dict(
                description="Spezialkäse für Waghalsige Käseliebhaber",
                sort_order=1,
                is_extra=True,
            )
        )
        extra_sub_size, _ = SubscriptionSize.objects.get_or_create(
            name="Spezialkäse Grösse",
            defaults=dict(
                long_name="8 Liter Abo",
                units=1,
                visible=True,
                depot_list=True,
                product=extra_sub_product,
            )
        )
        extra_sub_type1, _ = SubscriptionType.objects.get_or_create(
            name="Spezialkäse Einheitsgrösse",
            defaults=dict(
                size=extra_sub_size,
                description="Einmal pro Monat Überraschunskäse",
                sort_order=1,
                visible=True,
                required_assignments=1,
                price=300,
            )
        )
        BillingPeriod.objects.create(
            start_day=1,
            start_month=1,
            end_day=31,
            end_month=12,
            type=extra_sub_type1,
            cancel_day=30,
            cancel_month=9,
            price=120,
        )
        SubscriptionPart.objects.create(
            activation_date=datetime.date.today(),
            subscription=subscription_1,
            type=extra_sub_type1,
        )

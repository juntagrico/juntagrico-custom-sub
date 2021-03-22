# -*- coding: utf-8 -*-

from django import utils
from django.core.management.base import BaseCommand
from juntagrico import models as jm
from juntagrico.entity import subtypes as st
from juntagrico.entity.billing import ExtraSubBillingPeriod
from juntagrico.entity.depot import Depot
from juntagrico.entity.extrasubs import ExtraSubscriptionCategory, ExtraSubscriptionType
from juntagrico.entity.jobs import ActivityArea, JobType
from juntagrico.util import management as ja_mgmt

from juntagrico_custom_sub import models as csm


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        mem1_fields = {
            "first_name": "Boro",
            "last_name": "Sadler",
            "email": "boro@juntagrico.ch",
            "addr_street": "Mühlezelgstrasse 1",
            "addr_zipcode": "8047",
            "addr_location": "Zürich",
            "birthday": "2017-03-27",
            "phone": "079 123 45 99",
            "mobile_phone": "",
            "confirmed": True,
            "reachable_by_email": False,
            "inactive": False,
        }
        mem2_fields = {
            "first_name": "Deepak",
            "last_name": "Olvirsson",
            "email": "deepak@juntagico.ch",
            "addr_street": "Otto-Lang-Weg 1",
            "addr_zipcode": "8044",
            "addr_location": "Zürich",
            "birthday": "2017-03-27",
            "phone": "079 123 45 99",
            "mobile_phone": "",
            "confirmed": True,
            "reachable_by_email": False,
            "inactive": False,
        }
        member_1 = jm.Member.objects.create(**mem1_fields)
        member_2 = jm.Member.objects.create(**mem2_fields)
        share_all_fields = {
            "member": member_1,
            "paid_date": "2017-03-27",
            "issue_date": "2017-03-27",
            "booking_date": None,
            "cancelled_date": None,
            "termination_date": None,
            "payback_date": None,
            "number": None,
            "notes": "",
        }
        jm.Share.objects.create(**share_all_fields)
        jm.Share.objects.create(**share_all_fields)
        share_all_fields["member"] = member_2
        jm.Share.objects.create(**share_all_fields)
        jm.Share.objects.create(**share_all_fields)
        subprod_fields = {"name": "Milch"}
        subproduct = st.SubscriptionProduct.objects.create(**subprod_fields)
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
        subsize1 = st.SubscriptionSize.objects.create(**subsize1_fields)
        subsize3 = st.SubscriptionSize.objects.create(**subsize3_fields)
        subsize4 = st.SubscriptionSize.objects.create(**subsize4_fields)
        subtrype1_fields = {
            "name": "4 Liter",
            "long_name": "4 Liter Abo",
            "size": subsize1,
            "shares": 1,
            "visible": True,
            "required_assignments": 2,
            "price": 650,
            "description": "4 Liter Abo.",
        }
        subtrype3_fields = {
            "name": "8 Liter",
            "long_name": "8 Liter",
            "size": subsize3,
            "shares": 2,
            "visible": True,
            "required_assignments": 4,
            "price": 1200,
            "description": "8 Liter Abo.",
        }
        subtrype4_fields = {
            "name": "2 Liter",
            "long_name": "2 Liter",
            "size": subsize4,
            "shares": 0,
            "visible": True,
            "required_assignments": 1,
            "price": 300,
            "description": "2 Liter Abo.",
        }
        subtype1 = st.SubscriptionType.objects.create(**subtrype1_fields)
        subtype3 = st.SubscriptionType.objects.create(**subtrype3_fields)
        st.SubscriptionType.objects.create(**subtrype4_fields)
        depot1_fields = {
            "code": "D1",
            "name": "Toblerplatz",
            "weekday": 2,
            "latitude": "47.379308",
            "longitude": "8.559405",
            "addr_street": "Toblerstrasse 73",
            "addr_zipcode": "8044",
            "addr_location": "Zürich",
            "description": "Hinter dem Migros",
            "contact": member_2,
        }
        depot2_fields = {
            "code": "D2",
            "name": "Siemens",
            "weekday": 4,
            "latitude": "47.379173",
            "longitude": "8.495392",
            "addr_street": "Albisriederstrasse 207",
            "addr_zipcode": "8047",
            "addr_location": "Zürich",
            "description": "Hinter dem Restaurant Cube",
            "contact": member_1,
        }
        depot1 = Depot.objects.create(**depot1_fields)
        depot2 = Depot.objects.create(**depot2_fields)

        subscription_1 = ja_mgmt.create_subscription("2018-01-01", depot1, {subtype1: 1}, member_1)
        subscription_2 = ja_mgmt.create_subscription("2018-01-01", depot2, {subtype3: 1}, member_2)

        area1_fields = {
            "name": "Abpacken",
            "description": "Produkte abpacken",
            "core": False,
            "hidden": False,
            "coordinator": member_1,
            "show_coordinator_phonenumber": False,
        }
        area2_fields = {
            "name": "Ausfahren",
            "description": "Produkte ausfahren",
            "core": False,
            "hidden": False,
            "coordinator": member_2,
            "show_coordinator_phonenumber": False,
        }
        area_1 = ActivityArea.objects.create(**area1_fields)
        area_1.members.set([member_2])
        area_1.save()
        area_2 = ActivityArea.objects.create(**area2_fields)
        area_2.members.set([member_1])
        area_2.save()
        type1_fields = {
            "name": "Abpacken",
            "displayed_name": "",
            "description": "the real deal",
            "activityarea": area_1,
            "duration": 2,
            "location": "auf dem Hof",
        }
        type2_fields = {
            "name": "Ausfahren",
            "displayed_name": "",
            "description": "the real deal",
            "activityarea": area_2,
            "duration": 2,
            "location": "auf dem Hof",
        }
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {
            "slots": 10,
            "time": utils.timezone.now(),
            "pinned": False,
            "reminder_sent": False,
            "canceled": False,
            "type": type_1,
        }
        for x in range(0, 10):
            delta = utils.timezone.timedelta(days=7)
            job1_all_fields["time"] += delta
            jm.RecuringJob.objects.create(**job1_all_fields)  # warning

        job2_all_fields = {
            "slots": 10,
            "time": utils.timezone.now(),
            "pinned": False,
            "reminder_sent": False,
            "canceled": False,
            "type": type_2,
        }
        for x in range(0, 10):
            delta = utils.timezone.timedelta(days=7)
            job1_all_fields["time"] += delta
            jm.RecuringJob.objects.create(**job2_all_fields)  # warning

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

        subcontent1_fields = {"subscription": subscription_1}
        subcontent2_fields = {"subscription": subscription_2}
        subcontent1 = csm.SubscriptionContent.objects.create(**subcontent1_fields)
        subcontent2 = csm.SubscriptionContent.objects.create(**subcontent2_fields)

        subcontentitem1_fields = {
            "subscription_content": subcontent1,
            "product": wochenkase_klein,
            "amount": 1,
        }
        subcontentitem2_fields = {
            "subscription_content": subcontent2,
            "product": wochenkase_gross,
            "amount": 1,
        }
        csm.SubscriptionContentItem.objects.create(**subcontentitem1_fields)
        csm.SubscriptionContentItem.objects.create(**subcontentitem2_fields)

        csm.SubscriptionContentFutureItem.objects.create(**subcontentitem1_fields)
        csm.SubscriptionContentFutureItem.objects.create(**subcontentitem2_fields)

        # add extra subscriptions (Zusatzabos)
        extra_sub_cat1 = ExtraSubscriptionCategory.objects.create(
            name="Spezialkäse",
            description="Spezialkäse für Waghalsige Käseliebhaber",
            sort_order=1,
            visible=True,
        )
        extra_sub_type1 = ExtraSubscriptionType.objects.create(
            name="Spezialkäse Einheitsgrösse",
            size="Einheitsgrösse",
            description="Einmal pro Monat Überraschunskäse",
            sort_order=1,
            category_id=extra_sub_cat1.id,
            visible=True,
        )
        ExtraSubBillingPeriod.objects.create(
            start_day=1,
            start_month=1,
            end_day=31,
            end_month=12,
            type_id=extra_sub_type1.id,
            cancel_day=30,
            cancel_month=9,
            price=120,
        )
        jm.ExtraSubscription.objects.create(
            active=True,
            canceled=False,
            activation_date=utils.timezone.now(),
            main_subscription_id=subscription_1.id,
            type_id=extra_sub_type1.id,
        )

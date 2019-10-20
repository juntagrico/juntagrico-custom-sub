# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from juntagrico.models import *
from juntagrico_custom_sub.models import *


class Command(BaseCommand):

    # entry point used by manage.py
    def handle(self, *args, **options):
        mem1_fields = {'first_name': 'Boro', 'last_name': 'Sadler', 'email': 'boro@juntagrico.ch',
                       'addr_street': 'Mühlezelgstrasse 1', 'addr_zipcode': '8047', 'addr_location': 'Zürich',
                       'birthday': '2017-03-27', 'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False, 'inactive': False}
        mem2_fields = {'first_name': 'Deepak', 'last_name': 'Olvirsson',
                       'email': 'deepak@juntagico.ch', 'addr_street': 'Otto-Lang-Weg 1',
                       'addr_zipcode': '8044', 'addr_location': 'Zürich', 'birthday': '2017-03-27',
                       'phone': '079 123 45 99', 'mobile_phone': '', 'confirmed': True,
                       'reachable_by_email': False, 'inactive': False}
        member_1 = Member.objects.create(**mem1_fields)
        member_2 = Member.objects.create(**mem2_fields)
        share_all_fields = {'member': member_1, 'paid_date': '2017-03-27', 'issue_date': '2017-03-27', 'booking_date': None,
                            'cancelled_date': None, 'termination_date': None, 'payback_date': None, 'number': None,
                            'notes': ''}
        Share.objects.create(**share_all_fields)
        Share.objects.create(**share_all_fields)
        share_all_fields['member'] = member_2
        Share.objects.create(**share_all_fields)
        Share.objects.create(**share_all_fields)
        subprod_fields = {'name': 'Milch'}
        subproduct = SubscriptionProduct.objects.create(**subprod_fields)
        subsize1_fields = {'name': '4 Liter', 'long_name': '4 Liter Abo', 'units': 4, 'visible': True,
                          'depot_list': True, 'product': subproduct,
                          'description': '4 Liter Abo enthält Produkte die 4 Liter Milch entsprechen.'}
        subsize3_fields = {'name': '8 Liter', 'long_name': '8 Liter Abo', 'units': 8, 'visible': True,
                          'depot_list': True, 'product': subproduct,
                          'description': '8 Liter Abo enthält Produkte die 8 Liter Milch entsprechen.'}
        subsize4_fields = {'name': '2 Liter', 'long_name': '2 Liter Abo', 'units': 2, 'visible': True,
                          'depot_list': True, 'product': subproduct,
                          'description': '2 Liter Abo enthält Produkte die 2 Liter Milch entsprechen.'}                  
        subsize1 = SubscriptionSize.objects.create(**subsize1_fields)
        subsize3 = SubscriptionSize.objects.create(**subsize3_fields)
        subsize4 = SubscriptionSize.objects.create(**subsize4_fields)
        subtrype1_fields = {'name': '4 Liter', 'long_name': '4 Liter Abo', 'size': subsize1, 'shares': 1,
                          'visible': True, 'required_assignments': 2, 'price': 650,
                          'description': '4 Liter Abo.'}
        subtrype3_fields = {'name': '8 Liter', 'long_name': '8 Liter', 'size': subsize3, 'shares': 2,
                          'visible': True, 'required_assignments': 4, 'price': 1200,
                          'description': '8 Liter Abo.'}
        subtrype4_fields = {'name': '2 Liter', 'long_name': '2 Liter', 'size': subsize4, 'shares': 0,
                          'visible': True, 'required_assignments': 1, 'price': 300,
                          'description': '2 Liter Abo.'}
        subtype1 = SubscriptionType.objects.create(**subtrype1_fields)
        subtype3 = SubscriptionType.objects.create(**subtrype3_fields)
        subtype4 = SubscriptionType.objects.create(**subtrype4_fields)
        depot1_fields = {'code': 'D1', 'name': 'Toblerplatz', 'weekday': 2, 'latitude': '47.379308',
                         'longitude': '8.559405', 'addr_street': 'Toblerstrasse 73', 'addr_zipcode': '8044',
                         'addr_location': 'Zürich', 'description': 'Hinter dem Migros', 'contact': member_2}
        depot2_fields = {'code': 'D2', 'name': 'Siemens', 'weekday': 4, 'latitude': '47.379173',
                         'longitude': '8.495392', 'addr_street': 'Albisriederstrasse 207', 'addr_zipcode': '8047',
                         'addr_location': 'Zürich', 'description': 'Hinter dem Restaurant Cube', 'contact': member_1}
        depot1 = Depot.objects.create(**depot1_fields)
        depot2 = Depot.objects.create(**depot2_fields)
        sub_1_fields = {'depot': depot1,'primary_member': member_1, 'future_depot': None, 'active': True,
                        'activation_date': '2017-03-27', 'deactivation_date': None, 'creation_date': '2017-03-27',
                        'start_date': '2018-01-01'}
        sub_2_fields = {'depot': depot2,'primary_member': member_2, 'future_depot': None,
                        'active': True, 'activation_date': '2017-03-27', 'deactivation_date': None,
                        'creation_date': '2017-03-27', 'start_date': '2018-01-01'}
        subscription_1 = Subscription.objects.create(**sub_1_fields)
        member_1.subscription = subscription_1
        member_1.save()
        subscription_2 = Subscription.objects.create(**sub_2_fields)
        member_2.subscription = subscription_2
        member_2.save()
        TSST.objects.create(subscription=subscription_1, type=subtype1)
        TSST.objects.create(subscription=subscription_2, type=subtype3)
        TFSST.objects.create(subscription=subscription_1, type=subtype1)
        TFSST.objects.create(subscription=subscription_2, type=subtype3)

        area1_fields = {'name': 'Abpacken', 'description': 'Produkte abpacken', 'core': True,
                        'hidden': False, 'coordinator': member_1, 'show_coordinator_phonenumber': False}
        area2_fields = {'name': 'Ausfahren', 'description': 'Produkte ausfahren', 'core': False,
                        'hidden': False, 'coordinator': member_2, 'show_coordinator_phonenumber': False}
        area_1 = ActivityArea.objects.create(**area1_fields)
        area_1.members.set([member_2])
        area_1.save()
        area_2 = ActivityArea.objects.create(**area2_fields)
        area_2.members.set([member_1])
        area_2.save()
        type1_fields = {'name': 'Abpacken', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_1,
                        'duration': 2, 'location': 'auf dem Hof'}
        type2_fields = {'name': 'Ausfahren', 'displayed_name': '', 'description': 'the real deal', 'activityarea': area_2,
                        'duration': 2, 'location': 'auf dem Hof'}
        type_1 = JobType.objects.create(**type1_fields)
        type_2 = JobType.objects.create(**type2_fields)
        job1_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_1}
        for x in range(0, 10):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job1_all_fields)

        job2_all_fields = {'slots': 10, 'time': timezone.now(), 'pinned': False, 'reminder_sent': False,
                           'canceled': False, 'type': type_2}
        for x in range(0, 10):
            job1_all_fields['time'] += timezone.timedelta(days=7)
            RecuringJob.objects.create(**job2_all_fields)

        #CS specific
        prod1_fields = {'name': 'Milch', 'units': 1, 'unit_multiplier': 1,
                       'unit_name': 'Liter'}
        prod2_fields = {'name': 'Zusatzkäse', 'units': 2, 'unit_multiplier': 100,
                       'unit_name': 'Gramm'}
        prod3_fields = {'name': 'Quark', 'units': 1, 'unit_multiplier': 350,
                       'unit_name': 'Gramm'}
        prod4_fields = {'name': 'Fruchtyogurt', 'units': 1, 'unit_multiplier': 1,
                       'unit_name': 'Kilo'}
        prod5_fields = {'name': 'Natureyogurt', 'units': 1, 'unit_multiplier': 1,
                       'unit_name': 'Kilo'}
        prod6_fields = {'name': 'Wochenkäse klein', 'units': 2, 'unit_multiplier': 100,
                       'unit_name': 'Gramm','user_editable':False}     
        prod7_fields = {'name': 'Wochenkäse gross', 'units': 4, 'unit_multiplier': 100,
                       'unit_name': 'Gramm','user_editable':False}           
        Product.objects.create(**prod1_fields)
        Product.objects.create(**prod2_fields)
        Product.objects.create(**prod3_fields)
        Product.objects.create(**prod4_fields)
        Product.objects.create(**prod5_fields)
        wochenkase_klein = Product.objects.create(**prod6_fields)
        wochenkase_gross = Product.objects.create(**prod7_fields)

        mandatory1_fields = {'subscription_size': subsize1, 'product': wochenkase_klein, 'amount': 1}
        mandatory3_fields = {'subscription_size': subsize3, 'product': wochenkase_gross, 'amount': 1}
        SubscriptionSizeMandatoryProducts.objects.create(**mandatory1_fields)
        SubscriptionSizeMandatoryProducts.objects.create(**mandatory3_fields)

        subcontent1_fields = {'subscription':subscription_1}
        subcontent2_fields = {'subscription':subscription_2}
        subcontent1 = SubscriptionContent.objects.create(**subcontent1_fields)
        subcontent2 = SubscriptionContent.objects.create(**subcontent2_fields)

        subcontentitem1_fields = {'subscription_content':subcontent1,'product': wochenkase_klein, 'amount': 1}
        subcontentitem2_fields = {'subscription_content':subcontent2,'product': wochenkase_gross, 'amount': 1}
        SubscriptionContentItem.objects.create(**subcontentitem1_fields)
        SubscriptionContentItem.objects.create(**subcontentitem2_fields)

        SubscriptionContentFutureItem.objects.create(**subcontentitem1_fields)
        SubscriptionContentFutureItem.objects.create(**subcontentitem2_fields)







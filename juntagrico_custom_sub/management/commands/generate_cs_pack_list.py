from django.core.management.base import BaseCommand
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico_custom_sub.models import *
from juntagrico.models import *
from juntagrico.dao.depotdao import DepotDao
from django.db.models import Sum
from collections import defaultdict


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='force generation of depot list',
    )
    def handle(self, *args, **options):
        if not options['force'] and timezone.now().weekday() not in Config.depot_list_generation_days():
            print(
                'not the specified day for depot list generation, use --force to override')
            return
        depots = DepotDao.all_depots().order_by('weekday')
        products = Product.objects.all().order_by('id')
        latest_delivery = CustomDelivery.objects.all().order_by('-delivery_date')[0]

        #Rename products based on their name in the latest delivery
        for product in products:
            if latest_delivery.items.filter(product=product):
                product.name = latest_delivery.items.get(product=product).name
        depot_result = {}
        grouped_depots = {}
        for depot in depots:
            grouped_depots.setdefault(depot.weekday_name, []).append(depot)
        for weekday,depot_list in grouped_depots.items():
            depot_dict = {}
            for depot in depot_list:
                depot.fill_overview_cache()
                depot.fill_active_subscription_cache()
                amount_of_product = []
                for product in products:
                    productAmount = depot.subscription_cache.filter(content__products__product__id=product.id).aggregate(Sum('content__products__amount'))['content__products__amount__sum'] or 0
                    amount_of_product.append(productAmount)
                depot_dict[depot]=amount_of_product
            depot_result.setdefault(depot.weekday_name, []).append(depot_dict)
        renderdict = {
            'depots': depot_result,
            'products': products
        }
        render_to_pdf_storage('cs/exports/cs_packlist.html',
                              renderdict, 'depot_overview.pdf')

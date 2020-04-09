from django.core.management.base import BaseCommand
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico_custom_sub.models import *
from juntagrico.models import *
from juntagrico.dao.depotdao import DepotDao
from juntagrico.config import Config
from django.db.models import Sum
from collections import defaultdict
from django.utils import timezone
import copy


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
        depots = CsDepot.objects.all().order_by('weekday')
        products = Product.objects.all().order_by('code')
        latest_delivery = CustomDelivery.objects.all().order_by('-delivery_date')[0]

        #Rename products based on their name in the latest delivery
        deliveryProducts = []
        for product in products:
            if latest_delivery.items.filter(product=product):
                for deliveryProduct in latest_delivery.items.filter(product=product):
                    renamedProduct = copy.deepcopy(product)
                    renamedProduct.name = deliveryProduct.name
                    deliveryProducts.append(renamedProduct)
            else:
                deliveryProducts.append(product)
        grouped_depots = {}
        for depot in depots:
            grouped_depots.setdefault(depot.weekday_name, []).append(depot)
        totals = {}
        for weekday,depot_list in grouped_depots.items():
            total = [0]*len(deliveryProducts)
            for depot in depot_list:
                for idx,prod in enumerate(deliveryProducts):
                    total[idx] = total[idx]+depot.product_totals[prod]
            totals[weekday] = total
        renderdict = {
            'depots': grouped_depots,
            'products': deliveryProducts,
            'totals': totals
        }
        render_to_pdf_storage('cs/exports/cs_packlist.html',
                              renderdict, 'depot_overview.pdf')

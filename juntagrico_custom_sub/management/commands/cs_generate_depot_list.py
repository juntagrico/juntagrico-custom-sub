import copy

from django.core.management.base import BaseCommand
from django.utils import timezone
from juntagrico.config import Config
from juntagrico.util.pdf import render_to_pdf_storage

from juntagrico_custom_sub.entity.cs_depot import CsDepot
from juntagrico_custom_sub.entity.custom_delivery import CustomDelivery
from juntagrico_custom_sub.entity.product import Product


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
        depots = CsDepot.objects.all().filter(depot_list=True).order_by('sort_order')
        products = Product.objects.all().order_by('code')
        latest_delivery = CustomDelivery.objects.all().order_by('-delivery_date')[0]

        # Rename products based on their name in the latest delivery
        deliveryProducts = []
        for product in products:
            if latest_delivery.items.filter(product=product):
                for deliveryProduct in latest_delivery.items.filter(product=product):
                    renamedProduct = copy.deepcopy(product)
                    renamedProduct.name = deliveryProduct.name
                    deliveryProducts.append(renamedProduct)
            else:
                deliveryProducts.append(product)

        overallTotal = [0] * len(deliveryProducts)
        grouped_depots = {}
        for depot in depots:
            grouped_depots.setdefault(depot.weekday_name, []).append(depot)
        totals = {}
        for weekday, depot_list in grouped_depots.items():
            total = [0] * len(deliveryProducts)
            for depot in depot_list:
                product_totals = depot.product_totals
                for idx, prod in enumerate(deliveryProducts):
                    total[idx] = total[idx] + product_totals[prod]
                    overallTotal[idx] = overallTotal[idx] + product_totals[prod]
            totals[weekday] = total

        renderdict_depotlist = {
            'depots': depots,
            'products': deliveryProducts,
            'comment': latest_delivery.delivery_comment
        }
        render_to_pdf_storage('cs/exports/cs_depolist.html',
                              renderdict_depotlist, 'depotlist.pdf')

        renderdict_packlist = {
            'depots': grouped_depots,
            'products': deliveryProducts,
            'totals': totals,
            'overallTotals': overallTotal
        }
        render_to_pdf_storage('cs/exports/cs_packlist.html',
                              renderdict_packlist, 'depot_overview.pdf')

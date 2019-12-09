from django.core.management.base import BaseCommand
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico_custom_sub.models import *
from juntagrico.models import *
from juntagrico.dao.depotdao import DepotDao
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
        depots = CsDepot.objects.all().order_by('code')
        products = Product.objects.all().order_by('id')
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
        for depot in depots:
            depot.fill_overview_cache()
        renderdict = {
            'depots': depots,
            'products': deliveryProducts,
            'comment': latest_delivery.delivery_comment
        }
        render_to_pdf_storage('cs/exports/cs_depolist.html',
                              renderdict, 'depotlist.pdf')

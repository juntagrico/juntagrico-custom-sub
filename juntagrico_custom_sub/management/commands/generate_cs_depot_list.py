from django.core.management.base import BaseCommand
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico_custom_sub.models import *
from juntagrico.models import *

class Command(BaseCommand):
    def handle(self, *args, **options):
        depots = Depot.objects.all().order_by('code')
        products = Product.objects.all().order_by('id')
        for depot in depots:
            depot.fill_overview_cache()
            depot.fill_active_subscription_cache()
        renderdict = {
            'depots': depots,
            'products': products
        }
        render_to_pdf_storage('cs/exports/cs_depolist.html',
                              renderdict, 'cs_depolist.pdf')
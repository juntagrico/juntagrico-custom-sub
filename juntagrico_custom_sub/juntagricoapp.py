from django.apps import AppConfig
from juntagrico_custom_sub.admin import MandatoryProductInline

class JuntagricoCustomSub(AppConfig):
    name = 'juntagrico_custom_sub'
    verbose_name = "Juntagrico custom sub"

def subsize_inlines():
    return [MandatoryProductInline]

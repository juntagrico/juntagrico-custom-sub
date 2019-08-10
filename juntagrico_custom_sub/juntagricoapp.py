from django.apps import AppConfig
from juntagrico.util import addons
from juntagrico.entity.subtypes import SubscriptionSize
from juntagrico_custom_sub.admin import MandatoryProductInline

class JuntagricoCustomSub(AppConfig):
    name = 'juntagrico_custom_sub'
    verbose_name = "Juntagrico custom sub"

addons.config.register_model_inline(SubscriptionSize, MandatoryProductInline)
addons.config.register_sub_overview('cs/subscription_content_overview.html')
addons.config.register_sub_change('cs/subscription_content_change.html')
addons.config.register_admin_menu('cs/menu_content_change.html')


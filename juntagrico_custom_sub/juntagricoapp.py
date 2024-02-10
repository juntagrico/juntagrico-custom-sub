from juntagrico.entity.subtypes import SubscriptionSize
from juntagrico.util import addons

import juntagrico_custom_sub
from juntagrico_custom_sub.admin import MandatoryProductInline


addons.config.register_model_inline(SubscriptionSize, MandatoryProductInline)
addons.config.register_sub_overview('cs/hooks/subscription_content_overview.html')
addons.config.register_sub_change('cs/hooks/subscription_content_change.html')
addons.config.register_admin_menu('cs/hooks/menu_content_change.html')
addons.config.register_version(juntagrico_custom_sub.name, juntagrico_custom_sub.version)

from django.apps import AppConfig


class JuntagricoCustomSubAppconfig(AppConfig):
    name = "juntagrico_custom_sub"
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from juntagrico.util import addons
        addons.config.register_version(self.name)

        # for compatibility to downgraded subscription views
        addons.config.register_sub_overview('cs/hooks/subscription_content_overview.html')
        addons.config.register_sub_change('cs/hooks/subscription_content_change.html')

        # Basimilch specific
        from juntagrico.forms import SubscriptionPartBaseForm
        from juntagrico_custom_sub.basimilch import quantity_error
        SubscriptionPartBaseForm.validators.append(quantity_error)

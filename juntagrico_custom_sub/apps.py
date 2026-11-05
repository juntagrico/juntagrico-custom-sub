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

        # subscription content is defined per subscription, so all its parts must share the same delivery rhythm
        from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInline
        from juntagrico.forms import SubscriptionPartBaseForm
        from juntagrico_custom_sub.validators import consistent_rhythm, ConsistentRhythmSubscriptionPartInlineFormset
        SubscriptionPartBaseForm.validators.append(consistent_rhythm)
        SubscriptionPartInline.formset = ConsistentRhythmSubscriptionPartInlineFormset

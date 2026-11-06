from juntagrico.admins.inlines.subscription_part_inlines import SubscriptionPartInlineFormset
from juntagrico.entity.subtypes import SubscriptionType

from juntagrico_custom_sub.util.interval import check_consistent_rhythm


def consistent_rhythm(form):
    """
    Ensures that the regular parts of a subscription keep a common delivery rhythm.
    Canceled parts are ignored, as they will end.
    """
    if hasattr(form, 'part'):
        # change form: form.part gets replaced by the newly chosen type
        type_id = getattr(form, 'cleaned_data', {}).get('part_type')
        if not type_id:
            return
        new_types = [SubscriptionType.objects.get(pk=type_id)]
        existing_parts = form.part.subscription.future_parts.exclude(pk=form.part.pk)
    else:
        # signup and order forms: no subscription yet (signup) or parts are added to it (order)
        new_types = [sub_type for sub_type, amount in form.get_selected().items() if amount]
        subscription = getattr(form, 'subscription', None)
        existing_parts = subscription.future_parts if subscription else []
    check_consistent_rhythm(new_types + [part.type for part in existing_parts])


class ConsistentRhythmSubscriptionPartInlineFormset(SubscriptionPartInlineFormset):
    """
    same check for the subscription parts inline in the subscription admin
    """
    def clean(self):
        super().clean()
        check_consistent_rhythm([
            form.cleaned_data['type'] for form in self.forms
            if form.cleaned_data.get('type') is not None
            and not form.cleaned_data.get('DELETE', False)
            and form.cleaned_data.get('cancellation_date', form.instance.cancellation_date) is None
        ])

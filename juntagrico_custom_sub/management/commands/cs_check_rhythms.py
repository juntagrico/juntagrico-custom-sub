from django.core.management.base import BaseCommand
from juntagrico.entity.subs import Subscription

from juntagrico_custom_sub.util.interval import rhythms


class Command(BaseCommand):
    help = ("Lists subscriptions whose regular, not canceled parts have different delivery rhythms (interval/offset). "
            "For those, the depot list includes the subscription content whenever any of its parts is due.")

    def handle(self, *args, **options):
        subscriptions = Subscription.objects.filter(deactivation_date=None).prefetch_related('parts__type')
        for subscription in subscriptions:
            found = rhythms(part.type for part in subscription.parts.all()
                            if part.cancellation_date is None and part.deactivation_date is None)
            if len(found) > 1:
                described = ', '.join(f'every {i} week(s), offset {o}' for i, o in sorted(found))
                self.stdout.write(f'{subscription.pk}: {subscription} ({described})')

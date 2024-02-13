from django.core.exceptions import ValidationError
from juntagrico.entity.subtypes import SubscriptionType


def quantity_error(form):
    """
    validates the selected quantities for Basimilch's usecase
    selected is a dictionnary with SubscriptionType objects as keys and amounts as values
    """
    present4 = 0
    present8 = 0
    present2 = 0

    if hasattr(form, 'subscription'):
        active_parts = form.subscription.active_and_future_parts
        present4 = active_parts.filter(type__size__units=4).count()
        present8 = active_parts.filter(type__size__units=8).count()
        present2 = active_parts.filter(type__size__units=2).count()

    selected = form.get_selected()
    selected4 = selected[SubscriptionType.objects.get(size__units=4)]
    selected8 = selected[SubscriptionType.objects.get(size__units=8)]
    selected2 = selected[SubscriptionType.objects.get(size__units=2)]

    totalNew4 = present4 + selected4
    totalNew8 = present8 + selected8
    totalNew2 = present2 + selected2

    total_liters = totalNew4 * 4 + totalNew8 * 8 + totalNew2 * 2
    if total_liters == 2:
        raise ValidationError("Falls ein Abo gewünscht ist, müssen mindestens 4 Liter in einem Abo sein.")
    required8 = total_liters // 8
    required4 = (total_liters % 8) // 4
    if not (totalNew8 == required8 and totalNew4 == required4):
        raise ValidationError(
            "Du musst immer die grösstmögliche Abogrösse nehmen. "
            "Es ist zum Beispiel nicht möglich, 8 Liter auf zwei Vierliter-Abos aufzuteilen."
        )

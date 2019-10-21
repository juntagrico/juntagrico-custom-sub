from juntagrico_custom_sub.models import SubscriptionSizeMandatoryProducts


def new_content_valid(subscription, request, products):
    totalUnits = 0
    for product in products:
        minimalAmountForProduct = 0
        for type in subscription.future_types.all():
            for mandatoryProduct in SubscriptionSizeMandatoryProducts.objects.filter(
                product=product, subscription_size=type.size
            ):
                minimalAmountForProduct += mandatoryProduct.amount
        productAmount = int(request.POST.get("amount" + str(product.id)))
        if productAmount < 0:
            return (False, "Mengen unter Null sind nicht erlaubt.")
        if productAmount < minimalAmountForProduct:
            return (False, "Mindestens " + str(minimalAmountForProduct) + " " + product.name + " benötigt.")
        totalUnits += productAmount * product.units
    if totalUnits > int(calculate_future_size(subscription)):
        return (False, "Dein Abo hat nicht genug Platz für alle Produkte.")
    if totalUnits < int(calculate_future_size(subscription)):
        return (False, "Nicht alle Einheiten zugewiesen.")
    return (True, "")


def calculate_future_size(subscription):
    result = 0
    for type in subscription.future_types.all():
        result += type.size.units
    return result


def calculate_current_size(subscription):
    result = 0
    for type in subscription.types.all():
        result += type.size.units
    return result

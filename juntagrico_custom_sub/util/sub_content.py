from juntagrico_custom_sub.models import SubscriptionSizeMandatoryProducts


def new_content_valid(future_types, custom_prods, products):
    totalUnits = 0
    total_units_required = sum([ft.size.units * amount for ft, amount in future_types.items()])
    for product in products:
        minimalAmountForProduct = 0
        for ft in future_types:
            for mandatoryProduct in SubscriptionSizeMandatoryProducts.objects.filter(
                    product=product, subscription_size=ft.size
            ):
                minimalAmountForProduct += mandatoryProduct.amount
        productAmount = 0 if product not in custom_prods else custom_prods[product]
        if productAmount < 0:
            return "Mengen unter Null sind nicht erlaubt."
        if productAmount < minimalAmountForProduct:
            return "Mindestens " + str(minimalAmountForProduct) + " " + product.name + " benötigt."
        totalUnits += productAmount * product.units
    if totalUnits > total_units_required:
        return "Dein Abo hat nicht genug Platz für alle Produkte."
    if totalUnits < total_units_required:
        return "Nicht alle Einheiten zugewiesen."
    return ""


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

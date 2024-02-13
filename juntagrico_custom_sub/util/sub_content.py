from juntagrico_custom_sub.entity.product import Product
from juntagrico_custom_sub.entity.subscription_size_mandatory_products import SubscriptionSizeMandatoryProducts


def new_content_valid(future_types, custom_prods, products=None):
    products = products or Product.objects.all()
    totalUnits = 0
    total_units_required = sum([ft.size.units * amount for ft, amount in future_types.items()])
    for product in products:
        minimalAmountForProduct = 0
        for sub_type in future_types:
            for mandatoryProduct in SubscriptionSizeMandatoryProducts.objects.filter(
                    product=product, subscription_size=sub_type.size
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
    for part in subscription.active_and_future_parts:
        result += part.type.size.units
    return result


def calculate_current_size(subscription):
    result = 0
    for part in subscription.active_parts:
        result += part.type.size.units
    return result

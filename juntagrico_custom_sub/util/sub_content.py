from juntagrico_custom_sub.entity.product import Product


def new_content_valid(total_units, custom_prods, products=None):
    products = products or Product.objects.all()
    totalUnits = 0
    for product in products:
        productAmount = custom_prods.get(product.id, 0)
        if productAmount < 0:
            return "Mengen unter Null sind nicht erlaubt."
        if productAmount < product.min_amount:
            return "Mindestens " + str(product.min_amount) + " " + product.name + " benötigt."
        totalUnits += productAmount * product.units
    if totalUnits > total_units:
        return "Dein Abo hat nicht genug Platz für alle Produkte."
    if totalUnits < total_units:
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

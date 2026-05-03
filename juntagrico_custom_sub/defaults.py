def depot_list_context(context):
    import copy
    from juntagrico_custom_sub import entity

    depots = entity.cs_depot.CsDepot.objects.all().filter(depot_list=True).order_by("sort_order")
    products = entity.product.Product.objects.all().order_by("code")
    latest_delivery = entity.custom_delivery.CustomDelivery.objects.order_by("-delivery_date").first()

    # Rename products based on their name in the latest delivery
    deliveryProducts = []
    for product in products:
        if latest_delivery and latest_delivery.items.filter(product=product):
            for deliveryProduct in latest_delivery.items.filter(product=product):
                renamedProduct = copy.deepcopy(product)
                renamedProduct.name = deliveryProduct.name
                deliveryProducts.append(renamedProduct)
        else:
            deliveryProducts.append(product)

    return {
        "depots": depots,
        "products": deliveryProducts,
        "comment": latest_delivery and latest_delivery.delivery_comment or '',
    }


def pack_list_context(context):
    from juntagrico.util.temporal import weekdays

    context = depot_list_context(context)
    deliveryProducts = context['products']

    overallTotal = [0] * len(deliveryProducts)
    grouped_depots = {}
    for depot in context['depots']:
        wd = weekdays[depot.weekday]
        grouped_depots.setdefault(wd, []).append(depot)
    totals = {}
    for weekday, depot_list in grouped_depots.items():
        total = [0] * len(deliveryProducts)
        for depot in depot_list:
            product_totals = depot.product_totals
            for idx, prod in enumerate(deliveryProducts):
                total[idx] = total[idx] + product_totals[prod]
                overallTotal[idx] = overallTotal[idx] + product_totals[prod]
        totals[weekday] = total

    return {
        "depots": grouped_depots,
        "products": deliveryProducts,
        "totals": totals,
        "overallTotals": overallTotal,
    }


DEPOT_LISTS = {
    'depotlist': {
        'template': 'cs/exports/cs_depolist.html',
        'extra_context': depot_list_context
    },
    'depot_overview': {
        'template': 'cs/exports/cs_packlist.html',
        'extra_context': pack_list_context
    },
}

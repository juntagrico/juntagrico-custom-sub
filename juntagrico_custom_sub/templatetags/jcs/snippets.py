from django import template

from juntagrico_custom_sub.entity.product import Product

register = template.Library()

@register.inclusion_tag('cs/snippets/content_summary.html')
def custom_product_summary(custom_products):
    products = {str(product.id): product for product in Product.objects.filter(id__in=custom_products.keys())}
    return {
        'custom_products': {
            products[product_id]: amount for product_id, amount in custom_products.items()
        }
    }

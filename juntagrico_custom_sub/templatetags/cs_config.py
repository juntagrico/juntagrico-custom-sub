from django import template

from juntagrico_custom_sub.config import Config

register = template.Library()


@register.simple_tag
def cs_vocabulary(key):
    return Config.vocabulary(key)

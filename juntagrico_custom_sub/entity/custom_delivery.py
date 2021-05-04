from django.db import models
from django.utils.translation import gettext as _

from juntagrico_custom_sub.entity.product import Product


class CustomDelivery(models.Model):
    delivery_date = models.DateField(_('Lieferdatum'))
    delivery_comment = models.TextField(_('Mitteilung'), default="", blank=True)

    def __str__(self):
        return u"%s" % (self.delivery_date)

    class Meta:
        verbose_name = _('Lieferung')
        verbose_name_plural = _('Lieferungen')


class CustomDeliveryProduct(models.Model):
    delivery = models.ForeignKey(CustomDelivery, verbose_name=_('Lieferung'),
                                 related_name='items',
                                 on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_(
        'Produkt'), on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=100, default="")

    class Meta:
        verbose_name = _('Lieferobjekt')
        verbose_name_plural = _('Lieferobjekte')

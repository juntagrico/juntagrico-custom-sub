from django.core import validators
from django.db import models
from django.utils.translation import gettext as _
from juntagrico.entity.subtypes import SubscriptionSize


class Product(models.Model):
    name = models.CharField("Name", max_length=100)
    units = models.FloatField("Grösse", default=0)
    unit_multiplier = models.IntegerField("Grössen multiplikator", default=1)
    unit_name = models.CharField("Name Grösse", max_length=100, default="")
    mandatory_for_sizes = models.ManyToManyField(SubscriptionSize, related_name='mandatory_products',
                                                 through='juntagrico_custom_sub.SubscriptionSizeMandatoryProducts')
    user_editable = models.BooleanField("Menge durch Nutzer veränderbar", default=True)
    code = models.CharField('Sortier-Code', max_length=100, default='1', validators=[validators.validate_slug],
                            unique=True)

    @property
    def display_units(self):
        return int(self.unit_multiplier * self.units)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Produkt')
        verbose_name_plural = _('Produkte')

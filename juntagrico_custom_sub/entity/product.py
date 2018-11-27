from django.db import models

class Product(models.Model):
    name = models.CharField("Name",max_length=100)
    units = models.FloatField("Grösse",default=0)
    unit_multiplier = models.IntegerField("Grössen multiplikator",default=1)
    unit_name = models.CharField("Name Grösse",max_length=100,default="")
    @property
    def display_units(self):
        return int(self.unit_multiplier * self.units)
    def __str__(self):
        return self.name

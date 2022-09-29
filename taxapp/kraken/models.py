from django.db import models


class Price(models.Model):
    ts = models.IntegerField(default=0)
    XBTEUR = models.DecimalField(max_digits=10, decimal_places=2)
    ADAEUR = models.DecimalField(max_digits=10, decimal_places=8)
    DOTEUR = models.DecimalField(max_digits=10, decimal_places=8)
    ETHEUR = models.DecimalField(max_digits=10, decimal_places=5)



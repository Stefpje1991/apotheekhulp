from django.db import models

from accounts.models import Assistent, Apotheek


class LinkBetweenAssistentAndApotheek(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    apotheek = models.ForeignKey(Apotheek, on_delete=models.CASCADE)

    # New fields
    uurtarief = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fietsvergoeding = models.BooleanField(default=True)
    afstandInKilometers = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('assistent', 'apotheek')  # Ensure unique pairs
        verbose_name = 'Link Between Assistent and Apotheek'
        verbose_name_plural = 'Links Between Assistent and Apotheken'

    def __str__(self):
        return f'{self.assistent.user.email} - {self.apotheek.user.email}'

from django.db import models

from accounts.models import Assistent, Apotheek, User
from calendar_app.models import Event


class LinkBetweenAssistentAndApotheek(models.Model):
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    apotheek = models.ForeignKey(Apotheek, on_delete=models.CASCADE)

    # New fields
    uurtariefAssistent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    uurtariefApotheek = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kilometervergoeding = models.BooleanField(default=True)
    afstandInKilometers = models.IntegerField(blank=True, null=True)
    actief = models.BooleanField(default=True)

    class Meta:
        unique_together = ('assistent', 'apotheek')  # Ensure unique pairs
        verbose_name = 'Link Between Assistent and Apotheek'
        verbose_name_plural = 'Links Between Assistent and Apotheken'

    def __str__(self):
        return f'{self.assistent.user.email} - {self.apotheek.user.email}'


class InvoiceOverview(models.Model):
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    invoice_created_by = models.ForeignKey(Assistent, on_delete=models.CASCADE)
    invoice_created_at = models.DateTimeField(auto_now_add=True)
    invoice_amount = models.FloatField()
    invoice_btw = models.FloatField()
    invoice_paid = models.BooleanField(default=False)
    invoice_paid_at = models.DateTimeField(null=True, blank=True)
    invoice_paid_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    invoice_pdf = models.FileField(upload_to='invoices/assistent/', null=True, blank=True)

    class Meta:
        unique_together = ('invoice_number', 'invoice_created_by')
        verbose_name = 'Overview of invoice'
        verbose_name_plural = 'Overview of invoices'

    def __str__(self):
        return f'{self.invoice_number} - {self.invoice_created_by}'


class InvoiceDetail(models.Model):
    invoice_event = models.OneToOneField(Event, on_delete=models.CASCADE)
    invoice_subtotal = models.FloatField(default=0.00)
    invoice_id = models.ForeignKey(InvoiceOverview, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.invoice_id} - {self.invoice_event}'


class InvoiceApotheekOverview(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    invoice_created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoice_created_by')
    invoice_created_at = models.DateTimeField(auto_now_add=True)
    invoice_amount = models.FloatField()
    invoice_apotheek = models.ForeignKey(Apotheek, on_delete=models.CASCADE)
    invoice_btw = models.FloatField()
    invoice_paid = models.BooleanField(default=False)
    invoice_paid_at = models.DateTimeField(null=True, blank=True)
    invoice_paid_status_changed_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='invoice_paid_status_changed_by')
    invoice_pdf = models.FileField(upload_to='invoices/apotheek/', null=True, blank=True)

    class Meta:
        verbose_name = 'Overview of invoice'
        verbose_name_plural = 'Overview of invoices'

    def __str__(self):
        return f'{self.invoice_number} - {self.invoice_created_by}'


class InvoiceApotheekDetail(models.Model):
    invoice_event = models.OneToOneField(Event, on_delete=models.CASCADE)
    invoice_subtotal = models.FloatField(default=0.00)
    invoice_id = models.ForeignKey(InvoiceApotheekOverview, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.invoice_id} - {self.invoice_event}'

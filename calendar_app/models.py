from django.db import models

from accounts.models import User, Assistent, Apotheek


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('werk', 'Werk'),
        ('opleiding', 'Opleiding'),
        ('teambuilding', 'Teambuilding'),
        ('overleg', 'Overleg'),
        # Add more categories as needed
    ]

    STATUS_CHOICES = [
        ('accepted', 'Goedgekeurd'),
        ('noaction', 'Geen actie'),
        ('declined', 'Afgekeurd')
    ]

    STATUS_CHOICES_APOTHEEK = [
        ('accepted', 'Goedgekeurd'),
        ('noaction', 'Geen actie'),
        ('declined', 'Afgekeurd')
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    pauzeduur = models.SmallIntegerField(default=0, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='werk')
    assistent = models.ForeignKey(Assistent, on_delete=models.CASCADE, related_name='assistentevents', null=True,
                                  blank=True)
    apotheek = models.ForeignKey(Apotheek, on_delete=models.CASCADE, related_name='apotheekevents', null=True,
                                 blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userevents', null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='noaction')
    status_apotheek = models.CharField(max_length=50, choices=STATUS_CHOICES_APOTHEEK, default='noaction')
    status_apotheek_changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_user_changed', null=True, blank=True)
    invoiced = models.BooleanField(default=False)
    invoiced_to_apotheek = models.BooleanField(default=False)
    paid_by_apotheek = models.BooleanField(default=False)

    def __str__(self):
        return str(self.assistent) + "_" + str(self.apotheek) + "_" + str(self.start_time) + "_" + str(self.end_time)

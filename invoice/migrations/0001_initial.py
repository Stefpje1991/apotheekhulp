# Generated by Django 5.0.7 on 2024-08-08 12:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0006_remove_apotheek_apotheek_uurtarief_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkBetweenAssistentAndApotheek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uurtarief', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('fietsvergoeding', models.BooleanField(default=True)),
                ('afstandInKilometers', models.IntegerField(blank=True, null=True)),
                ('apotheek', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.apotheek')),
                ('assistent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.assistent')),
            ],
            options={
                'verbose_name': 'Link Between Assistent and Apotheek',
                'verbose_name_plural': 'Links Between Assistent and Apotheken',
                'unique_together': {('assistent', 'apotheek')},
            },
        ),
    ]

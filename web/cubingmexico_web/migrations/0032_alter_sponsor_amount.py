# Generated by Django 4.1.7 on 2023-10-13 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_web', '0031_donor_sponsor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, default='', max_digits=10, null=True, verbose_name='Monto donado'),
        ),
    ]

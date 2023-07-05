# Generated by Django 4.1.7 on 2023-06-07 00:14

import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_web', '0022_stateteam_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='stateteam',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=255, validators=[django.core.validators.EmailValidator()], verbose_name='Dirección de correo electrónico'),
        ),
        migrations.AlterField(
            model_name='stateteam',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Número de teléfono'),
        ),
    ]

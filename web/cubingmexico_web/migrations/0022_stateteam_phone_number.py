# Generated by Django 4.1.7 on 2023-05-15 00:38

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_web', '0021_alter_personstateteam_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='stateteam',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128, region=None, verbose_name='Número de teléfono'),
        ),
    ]

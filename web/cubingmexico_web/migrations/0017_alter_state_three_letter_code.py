# Generated by Django 4.1.7 on 2023-05-06 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_web', '0016_state_three_letter_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='state',
            name='three_letter_code',
            field=models.CharField(max_length=3),
        ),
    ]
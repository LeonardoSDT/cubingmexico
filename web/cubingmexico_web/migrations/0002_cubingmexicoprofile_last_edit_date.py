# Generated by Django 4.1.7 on 2023-05-04 03:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cubingmexicoprofile',
            name='last_edit_date',
            field=models.DateField(default=datetime.date(2023, 5, 1)),
        ),
    ]

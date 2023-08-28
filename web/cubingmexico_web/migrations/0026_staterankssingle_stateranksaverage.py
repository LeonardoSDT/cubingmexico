# Generated by Django 4.1.7 on 2023-08-28 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cubingmexico_wca', '0001_initial'),
        ('cubingmexico_web', '0025_alter_competitionstate_competition'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateRanksSingle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_rank', models.IntegerField()),
                ('rankssingle', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cubingmexico_wca.rankssingle')),
            ],
        ),
        migrations.CreateModel(
            name='StateRanksAverage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state_rank', models.IntegerField()),
                ('ranksaverage', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cubingmexico_wca.ranksaverage')),
            ],
        ),
    ]
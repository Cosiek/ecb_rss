# Generated by Django 2.1.7 on 2019-03-17 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3, unique=True, verbose_name='Nazwa')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=4, max_digits=8, verbose_name='Wartość względem EUR')),
                ('value_time', models.DateTimeField(verbose_name='Stan na czas')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='currency.Currency')),
            ],
        ),
    ]
# Generated by Django 2.1.3 on 2018-12-06 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KData',
            fields=[
                ('date', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('ts_code', models.CharField(max_length=10)),
                ('open', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('vol', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'k_data',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Latest',
            fields=[
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('id', models.IntegerField(blank=True, null=True)),
                ('datetime', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'latest',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Senti',
            fields=[
                ('datetime', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
                ('pos', models.IntegerField(blank=True, null=True)),
                ('neg', models.IntegerField(blank=True, null=True)),
                ('neu', models.IntegerField(blank=True, null=True)),
                ('posscore', models.FloatField(blank=True, null=True)),
                ('negscore', models.FloatField(blank=True, null=True)),
                ('neuscore', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'senti',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SentiDaily',
            fields=[
                ('datetime', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
                ('pos', models.IntegerField(blank=True, null=True)),
                ('neg', models.IntegerField(blank=True, null=True)),
                ('neu', models.IntegerField(blank=True, null=True)),
                ('posscore', models.FloatField(blank=True, null=True)),
                ('negscore', models.FloatField(blank=True, null=True)),
                ('neuscore', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'senti_daily',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StockList',
            fields=[
                ('ts_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=10)),
                ('industry', models.CharField(max_length=10)),
                ('list_date', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'stock_list',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Words',
            fields=[
                ('datetime', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('text', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'words',
                'managed': False,
            },
        ),
    ]

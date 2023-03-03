# Generated by Django 4.1.7 on 2023-03-03 06:07

import checkout.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('identifier', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('totp', models.IntegerField(blank=True, null=True)),
                ('account_type', models.CharField(choices=[('RE', 'Reddit'), ('DI', 'Discord')], default='RE', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='AccountUsage',
            fields=[
                ('identifier', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('checkout_timestamp', models.DateTimeField(auto_now_add=True)),
                ('time_used', models.DateTimeField(blank=True, null=True)),
                ('checkin_timestamp', models.DateTimeField(auto_now=True)),
                ('lockout_interval', models.DurationField(default=datetime.timedelta(seconds=300))),
                ('account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='checkout.account')),
                ('request_token', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.token')),
            ],
        ),
        migrations.CreateModel(
            name='AccountToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout.account')),
            ],
        ),
        migrations.CreateModel(
            name='AccountBan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permanent', models.BooleanField(default=False)),
                ('year', models.PositiveSmallIntegerField(default=checkout.models.current_year)),
                ('report_date', models.DateField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout.account')),
            ],
        ),
    ]
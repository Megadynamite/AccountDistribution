import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
# Create your models here.
from django.utils import timezone
from django.utils.datetime_safe import strftime


class Account(models.Model):
    def __str__(self):
        return f'{self.get_account_type_display()} | {self.username}'

    identifier = models.UUIDField(default=uuid.uuid4, primary_key=True)  # UUID
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                null=True)  # User that created account (Technically user that inserted account, may need a separate field)
    username = models.CharField(max_length=100, null=True, blank=True)  # Account username
    email = models.EmailField(null=True, blank=True) # Account email
    password = models.CharField(max_length=100, null=True, blank=True) # Account password
    account_types = [
        ('RE', 'Reddit'),
        ('DI', 'Discord'),
    ]
    totp = models.IntegerField(null=True, blank=True)
    account_type = models.CharField(
        max_length=2,
        choices=account_types,
        default='RE')


class AccountUsage(models.Model):
    def __str__(self):
        return f'{self.account.get_account_type_display()} | {self.account.username} | Lock Until: {strftime(self.time_used + self.lockout_interval, "%H:%M:%S %m/%d/%Y")} '

    identifier = models.UUIDField(default=uuid.uuid4, primary_key=True)
    account = models.ForeignKey('Account', on_delete=models.SET_NULL, null=True)
    checkout_timestamp = models.DateTimeField(auto_now_add=True)  # Store time account was checked out
    time_used = models.DateTimeField(default=timezone.now)  # Store time account was used
    checkin_timestamp = models.DateTimeField(auto_now=True)  # Store time account was checked in
    lockout_interval = models.DurationField(default=timedelta(minutes=5))  # Store timeout duration for account
    request_token = models.ForeignKey('authentication.Token', on_delete=models.CASCADE, null=True,
                                      blank=True)  # Store token that made request
    request_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # Store account that made request


def current_year():
    return timezone.now().year


class AccountBan(models.Model):
    def __str__(self):
        return f'{self.account.username.title()} | Year: {self.year} | Permanent: {self.permanent}'

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    permanent = models.BooleanField(default=False)
    year = models.PositiveSmallIntegerField(default=current_year)
    report_date = models.DateField(auto_now=True)


class AccountToken(models.Model):
    def __str__(self):
        return f'{self.account.username.title()}'

    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    token_type = models.CharField(max_length=32)

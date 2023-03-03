from django.contrib import admin

# Register your models here.

from .models import Account, AccountUsage, AccountToken, AccountBan

admin.site.register(Account)
admin.site.register(AccountUsage)
admin.site.register(AccountBan)
admin.site.register(AccountToken)

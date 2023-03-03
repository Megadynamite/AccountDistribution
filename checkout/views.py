import json
import uuid
from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.db import connection
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.core import serializers

# Create your views here.
from authentication.models import wrap_token_auth, Token
from checkout.models import Account, AccountUsage
from utils import dictfetchall


def checkout(request, account_type):
    token = None
    if not request.user.is_authenticated:
        token = wrap_token_auth(request)
        if token is None:
            return HttpResponse("Unauthorized", status=401)
        else:
            token = Token.objects.get(content=token)
    with connection.cursor() as cursor:
        cursor.execute("""SELECT account_id, username, email, password, content token, totp, account_type FROM
                                    (
                                        SELECT *, row_number() OVER (PARTITION BY account_id ORDER BY content DESC) row_number
                                        FROM checkout_accounttoken cs_outer LEFT JOIN checkout_account a on cs_outer.account_id = a.identifier
                                    ) sort
                                    WHERE row_number = 1
                                    AND account_id NOT IN (SELECT account_id FROM checkout_accountusage WHERE time_used + lockout_interval >= now())
                                    AND account_id NOT IN (SELECT account_id FROM checkout_accountban WHERE (extract(YEAR FROM now()) = year OR permanent))
                                    AND lower(account_type) = lower(%s)
                                    LIMIT %s
                                    ;""", [account_type, request.GET.get('count', 1)])
        data = dictfetchall(cursor)
    accounts_ids_return = [account_return['account_id'] for account_return in data]
    for i in range(0, len(accounts_ids_return)):
        account_id_return = accounts_ids_return[i]
        account_return = Account.objects.get(identifier=account_id_return)
        usage_uuid = uuid.uuid4()
        data[i]['request_identifier'] = usage_uuid
        account_object = AccountUsage(identifier=usage_uuid, account=account_return,
                                      lockout_interval=timedelta(minutes=10), request_token=token)
        account_object.save()
    return JsonResponse(data, safe=False)


def checkin(request):
    if not request.user.is_authenticated:
        token = wrap_token_auth(request)
        if token is None:
            return HttpResponse("Unauthorized", status=401)
    try:
        if 'request_identifier' in request.headers:
            account_usage = AccountUsage.objects.get(pk=request.headers.get())
            account_usage['identifier'] = request.headers['request_identifier']
            if 'time_used' in request.headers:
                account_usage['time_used'] = request.headers['time_used']
            if 'lock_duration' in request.headers:
                account_usage['lockout_interval'] = request.headers['lock_duration']
            account_usage.save()
    except (AccountUsage.DoesNotExist, ValueError):
        return HttpResponse("Bad Request", 400)

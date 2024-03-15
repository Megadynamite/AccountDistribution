import json
import uuid
from datetime import timedelta

from django.db import connection, IntegrityError
from django.http import HttpResponse, JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from authentication.models import wrap_token_auth, Token
from checkout.models import Account, AccountUsage, AccountToken
from utils import dictfetchall


@require_http_methods(["GET"])
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


@require_http_methods(["POST"])
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
        return HttpResponse("Bad Request", status=400)


@csrf_exempt
def create(request):
    if not request.user.is_authenticated:
        token = wrap_token_auth(request)
        if token is None:
            return HttpResponse("Unauthorized", status=401)
    identifier = request.POST.get('identifier', None)
    username = request.POST.get('username', None)
    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    token = request.POST.get('token', None)
    token_type = request.POST.get('type', None)
    account_type = request.POST.get('account_type', None)
    creator = request.POST.get('creator', None)
    new_account = Account(identifier=identifier, username=username, email=email, password=password,
                          account_type=account_type, creator=creator)
    new_token = AccountToken(account=new_account, content=token, token_type=token_type)
    try:
        new_account.save()
        new_token.save()
        return HttpResponse(status=200)
    except IntegrityError:
        return HttpResponse("Bad Request", status=400)

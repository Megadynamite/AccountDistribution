from django.http import HttpResponse

# Create your views here.
from authentication.models import Token


def revoke(request, token=None):
    if 'token' in request.headers or token is not None:
        if 'token' in request.headers:
            token = request.headers['token']
        try:
            invalidate_token = Token.objects.get(session_token=token)
            invalidate_token.enabled = False
            invalidate_token.save()
        except Token.DoesNotExist:
            pass
    return HttpResponse(status=200)

import secrets
import uuid

from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.utils import timezone

from checkout.models import Account


class UserData(models.Model):
    pass


def generate_secure():
    return secrets.token_urlsafe(64)


class Token(models.Model):
    def __str__(self):
        return self.owner.__str__().title()

    identifier = models.UUIDField(default=uuid.uuid4, primary_key=True)
    content = models.CharField(default=generate_secure, max_length=86)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expiration = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now=True)


class RedditBackend(BaseBackend):
    pass


class TokenBackend(BaseBackend):
    def authenticate(self, request, token=None):
        try:
            token = Token.objects.get(content=token)
            if token.enabled:
                if token.expiration is None:
                    return token.owner
                elif token.expiration > timezone.now():
                    return token.owner
            return None
        except Token.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def wrap_token_auth(request):
    # Function that reads token in headers
    if 'token' in request.headers:
        token = request.headers['token']
        user = authenticate(request, token=token)
        if user is not None:
            login(request, user, backend='authentication.models.TokenBackend')
            return token
    return None

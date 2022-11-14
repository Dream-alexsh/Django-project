from django.db import models

from core.models import User


class TgUser(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Chat ID', unique=True)
    username = models.CharField(max_length=255, verbose_name='Username', null=True, blank=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    verification_code = models.CharField(max_length=255, null=True, blank=True, default=None)
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from woningzoeker.fields import EncryptedJSONField


class NotificationProvider(models.Model):
    class Type(models.TextChoices):
        EMAIL = 'EMAIL'
        TELEGRAM = 'TELEGRAM'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    type = models.CharField(max_length=255, choices=Type.choices)
    credentials = EncryptedJSONField()

    user = models.ForeignKey(User, related_name='notification_providers', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {str(self.type)}'

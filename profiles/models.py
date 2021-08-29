from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from residences.models import City


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    birthdate = models.DateField()
    token = models.CharField(max_length=32, unique=True)
    min_price_base = models.PositiveIntegerField(default=0)
    max_price_base = models.PositiveIntegerField(default=0)

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    cities = models.ManyToManyField(City, related_name='profiles', blank=True)

    def __str__(self):
        return self.user.username

from uuid import uuid4

from django.db import models

from corporations.models import Corporation


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Residence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    street = models.CharField(max_length=255)
    number = models.CharField(max_length=16)
    postal_code = models.CharField(max_length=6)

    # TODO: external ID
    # TODO: residence type, area, rooms, etc.

    corporation = models.ForeignKey(Corporation, related_name='residences', on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name='residences', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.street} {self.number}, {self.postal_code} {self.city.name}'

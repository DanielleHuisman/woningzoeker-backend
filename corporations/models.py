from uuid import uuid4

from django.db import models


class Corporation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    name = models.CharField(max_length=255, unique=True)

    cities = models.ManyToManyField('residences.City', related_name='corporations')

    def __str__(self):
        return self.name

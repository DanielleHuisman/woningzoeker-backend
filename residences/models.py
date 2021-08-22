from uuid import uuid4

from django.db import models

from corporations.models import Corporation, Registration


class City(models.Model):
    class Meta:
        verbose_name_plural = 'cities'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Residence(models.Model):
    class Type(models.TextChoices):
        HOUSE_DETACHED = 'HOUSE_DETACHED',
        HOUSE_SEMI_DETACHED = 'HOUSE_SEMI_DETACHED',
        HOUSE_DUPLEX = 'HOUSE_DUPLEX',
        HOUSE_TERRACED = 'HOUSE_TERRACED',
        HOUSE_UNKNOWN = 'HOUSE_UNKNOWN',
        APARTMENT = 'APARTMENT',
        MAISONNETTE = 'MAISONNETTE'
        UNKNOWN = 'UNKNOWN'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    external_id = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)

    street = models.CharField(max_length=255)
    number = models.CharField(max_length=16)
    postal_code = models.CharField(max_length=6)
    neighbourhood = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, choices=Type.choices)
    price_base = models.PositiveIntegerField(blank=True, null=True)
    price_service = models.PositiveIntegerField(blank=True, null=True)
    price_benefit = models.PositiveIntegerField(blank=True, null=True)
    price_total = models.PositiveIntegerField()
    energy_label = models.CharField(max_length=1, blank=True, null=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    area = models.PositiveSmallIntegerField(blank=True, null=True)
    rooms = models.PositiveSmallIntegerField(blank=True, null=True)
    bedrooms = models.PositiveSmallIntegerField(blank=True, null=True)
    floor = models.PositiveSmallIntegerField(blank=True, null=True)
    has_elevator = models.BooleanField(blank=True, null=True)
    available_at = models.DateField(blank=True, null=True)
    reactions_ended_at = models.DateTimeField(blank=True, null=True)
    url = models.TextField()
    photo_url = models.TextField(blank=True, null=True)
    floor_plan_url = models.TextField(blank=True, null=True)

    corporation = models.ForeignKey(Corporation, related_name='residences', on_delete=models.CASCADE)
    city = models.ForeignKey(City, related_name='residences', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.street} {self.number}, {self.postal_code} {self.city.name}'


class Reaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)

    rank_number = models.PositiveSmallIntegerField(blank=True, null=True)

    residence = models.ForeignKey(Residence, related_name='reactions', on_delete=models.CASCADE)
    registration = models.ForeignKey(Registration, related_name='reactions', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.registration.identifier} - {str(self.residence)}'

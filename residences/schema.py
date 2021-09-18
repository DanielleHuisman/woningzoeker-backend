import graphene
from graphene_django import DjangoObjectType

from .models import City, Residence, Reaction


class CityType(DjangoObjectType):
    class Meta:
        model = City


class ResidenceType(DjangoObjectType):
    class Meta:
        model = Residence


class ReactionType(DjangoObjectType):
    class Meta:
        model = Reaction


class Query(graphene.ObjectType):
    city = graphene.Field(CityType, id=graphene.UUID())
    cities = graphene.List(CityType)

    residence = graphene.Field(ResidenceType, id=graphene.UUID())
    residences = graphene.List(ResidenceType)

    reaction = graphene.Field(ReactionType, id=graphene.UUID())

    def resolve_city(self, _info, **kwargs):
        return City.objects.get(id=kwargs['id'])

    def resolve_cities(self, _info):
        return City.objects.all()

    def resolve_residence(self, _info, **kwargs):
        return Residence.objects.get(id=kwargs['id'])

    def resolve_residences(self, _info):
        return Residence.objects.all()

    def resolve_reaction(self, _info, **kwargs):
        return Reaction.objects.get(id=kwargs['id'])

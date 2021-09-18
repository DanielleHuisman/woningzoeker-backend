import graphene
from graphene_django import DjangoObjectType

from .models import Platform, Corporation, Registration


class PlatformType(DjangoObjectType):
    class Meta:
        model = Platform


class CorporationType(DjangoObjectType):
    class Meta:
        model = Corporation


class RegistrationType(DjangoObjectType):
    class Meta:
        model = Registration
        exclude = ('credentials', )


class Query(graphene.ObjectType):
    platform = graphene.Field(PlatformType, id=graphene.UUID())
    platforms = graphene.List(PlatformType)

    corporation = graphene.Field(CorporationType, id=graphene.UUID())
    corporations = graphene.List(CorporationType)

    registration = graphene.Field(RegistrationType, id=graphene.UUID())

    def resolve_platform(self, _info, **kwargs):
        return Platform.objects.get(id=kwargs['id'])

    def resolve_platforms(self, _info):
        return Platform.objects.all()

    def resolve_corporation(self, _info, **kwargs):
        return Corporation.objects.get(id=kwargs['id'])

    def resolve_corporations(self, _info):
        return Corporation.objects.all()

    def resolve_registration(self, _info, **kwargs):
        return Registration.objects.get(id=kwargs['id'])

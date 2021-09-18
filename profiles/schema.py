import graphene
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from graphene_django import DjangoObjectType

from .models import Profile


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('password', )


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.UUID())

    profile = graphene.Field(ProfileType, id=graphene.UUID())

    def resolve_user(self, info, **kwargs):
        if info.context.user.id != kwargs['id']:
            raise PermissionDenied()
        return User.objects.get(id=kwargs['id'])

    def resolve_profile(self, info, **kwargs):
        if hasattr(info.context.user, 'profile') and info.context.user.profile.id != kwargs['id']:
            raise PermissionDenied()
        return Profile.objects.get(id=kwargs['id'])

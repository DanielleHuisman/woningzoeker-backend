from django.contrib.admin import register, ModelAdmin

from .models import Platform, Corporation, Registration


@register(Platform)
class PlatformAdmin(ModelAdmin):
    list_display = ['id', 'name', 'handle', 'corporation_count', 'registration_count']
    list_filter = []

    def corporation_count(self, platform):
        return platform.corporations.count()

    def registration_count(self, platform):
        return platform.registrations.count()


@register(Corporation)
class CorporationAdmin(ModelAdmin):
    list_display = ['id', 'name', 'handle', 'city_count', 'residence_count']
    list_filter = ['cities']

    def city_count(self, corporation):
        return corporation.cities.count()

    def residence_count(self, corporation):
        return corporation.residences.count()


@register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = ['id', 'user', 'platform', 'identifier', 'reaction_count']
    list_filter = ['user', 'platform']

    def reaction_count(self, registration):
        return registration.reactions.count()

    # TODO: hide credentials field, but allow updating

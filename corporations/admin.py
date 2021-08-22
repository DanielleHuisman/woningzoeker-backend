from django.contrib.admin import register, ModelAdmin

from .models import Corporation, Registration


@register(Corporation)
class CorporationAdmin(ModelAdmin):
    list_display = ['id', 'name', 'handle', 'city_count', 'residence_count', 'registration_count']
    list_filter = ['cities']

    def city_count(self, corporation):
        return corporation.cities.count()

    def residence_count(self, corporation):
        return corporation.residences.count()

    def registration_count(self, corporation):
        return corporation.registrations.count()


@register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = ['id', 'user', 'corporation', 'identifier']
    list_filter = ['user', 'corporation']

    # TODO: hide credentials field, but allow updating

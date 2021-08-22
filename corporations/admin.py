from django.contrib.admin import register, ModelAdmin

from .models import Corporation, Registration


@register(Corporation)
class CorporationAdmin(ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['cities']


@register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = ['id', 'user', 'corporation', 'identifier']
    list_filter = ['user', 'corporation']

    # TODO: hide credentials field, but allow updating

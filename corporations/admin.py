from django.contrib.admin import register, ModelAdmin

from .models import Corporation


@register(Corporation)
class CorporationAdmin(ModelAdmin):
    list_display = ['id', 'name']
    list_filter = []

from django.contrib.admin import register, ModelAdmin

from .models import City, Residence, Reaction


@register(City)
class CityAdmin(ModelAdmin):
    list_display = ['id', 'name']
    list_filter = []


@register(Residence)
class ResidenceAdmin(ModelAdmin):
    list_display = ['id', 'city', 'corporation', 'street', 'number', 'postal_code', 'type', 'price_total', 'reactions_ended_at']
    list_filter = ['city', 'corporation', 'type', 'created_at', 'reactions_ended_at']


@register(Reaction)
class ReactionAdmin(ModelAdmin):
    list_display = ['id', 'user', 'residence', 'rank_number']
    list_filter = ['user']

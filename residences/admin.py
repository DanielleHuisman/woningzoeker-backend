from django.contrib.admin import register, ModelAdmin

from .models import City, Residence, Reaction


@register(City)
class CityAdmin(ModelAdmin):
    list_display = ['id', 'name', 'corporation_count', 'residence_count']
    list_filter = []

    def corporation_count(self, city):
        return city.corporations.count()

    def residence_count(self, city):
        return city.residences.count()


@register(Residence)
class ResidenceAdmin(ModelAdmin):
    list_display = ['id', 'city', 'corporation', 'street', 'number', 'postal_code', 'type', 'price_total', 'reactions_ended_at', 'reaction_count']
    list_filter = ['city', 'corporation', 'type', 'created_at', 'reactions_ended_at']

    def reaction_count(self, residence):
        return residence.reactions.count()


@register(Reaction)
class ReactionAdmin(ModelAdmin):
    list_display = ['id', 'registration', 'residence', 'rank_number']
    list_filter = ['registration']

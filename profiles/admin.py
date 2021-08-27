from django.contrib.admin import register, ModelAdmin

from .models import Profile


@register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ['id', 'user', 'birthdate', 'min_price', 'max_price']
    list_filter = []

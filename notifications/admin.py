from django.contrib.admin import register, ModelAdmin

from .models import NotificationProvider


@register(NotificationProvider)
class NotificationProviderAdmin(ModelAdmin):
    list_display = ['id', 'user', 'type', 'identifier']
    list_filter = ['type']

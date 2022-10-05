from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from .models import Client, Message, MobileCode, Notification, Tag

ModelAdmin.empty_value_display = '-пусто-'


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(MobileCode)
class MobileCode(admin.ModelAdmin):
    list_display = ('id', 'mobile_code')
    search_fields = ('mobile_code',)
    list_filter = ('mobile_code',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'telephone', 'mobile_code', 'get_tag', 'timezone')
    search_fields = ('telephone',)
    list_filter = ('telephone', 'tag')

    def get_tag(self, obj):
        return ', '.join(
            [str(tags) for tags in obj.tag.all()]
        )
    get_tag.short_description = 'Тег'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date_time_start', 'text', 'date_time_stop',
        'get_mobile_code', 'get_tag', 'time_interval'
    )
    search_fields = ('text',)
    list_filter = ('date_time_start',)

    def get_tag(self, obj):
        return ', '.join(
            [str(tags) for tags in obj.tag.all()]
        )
    get_tag.short_description = 'Теги'

    def get_mobile_code(self, obj):
        return '\n'.join(
            [str(mobile_code) for mobile_code in obj.mobile_code.all()]
        )
    get_mobile_code.short_description = 'Код моб.оператора'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'pub_date', 'status', 'notification', 'get_clients')
    search_fields = ('status',)
    list_filter = ('notification',)

    def get_clients(self, obj):
        return '\n'.join(
            [str(clients) for clients in obj.clients.all()]
        )
    get_clients.short_description = 'Клиенты'

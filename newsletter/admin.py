from django.contrib import admin
from .models import Client, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'comment',)
    search_fields = ('name', 'email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'text_message',)
    search_fields = ('subject', 'text_message',)
    list_filter = ('subject', 'text_message',)
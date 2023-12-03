from django.contrib import admin
from .models import *

admin.site.register(Room)

class MessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'message']

admin.site.register(Message, MessageAdmin)
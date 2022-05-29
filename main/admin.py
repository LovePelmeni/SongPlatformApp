from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.CustomUser)
class UserModelAdmin(admin.ModelAdmin):

    list_display = ['username', 'phone_number', 'password', 'email']
    fields = ['username', 'phone_number', 'password', 'email']

@admin.register(models.Video)
class VideoAdmin(admin.ModelAdmin):

    list_display = ['name', 'created_at']
    fields = ['name', 'created_at']

@admin.register(models.ChatGroup)
class GroupAdmin(admin.ModelAdmin):

    list_display = ['group_name', 'last_updated']
    fields = ['group_name', 'last_updated']




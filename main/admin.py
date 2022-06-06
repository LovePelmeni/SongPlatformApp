from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.CustomUser)
class UserModelAdmin(admin.ModelAdmin):

    list_display = ['username', 'phone_number', 'password', 'email']
    fields = ['username', 'phone_number', 'password', 'email']

@admin.register(models.Song)
class SongModelAdmin(admin.ModelAdmin):

    list_display = ('song_name', 'song_description',)
    fields = ('song_name', 'song_description',)

@admin.register(models.Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    pass




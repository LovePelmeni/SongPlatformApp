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

    list_display = ('subscription_name',)
    fields = ('subscription_name',)

@admin.register(models.Album)
class AlbumModelAdmin(admin.ModelAdmin):

    list_display = ('album_name',)
    fields = ('album_name',)



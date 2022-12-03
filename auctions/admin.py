from django.contrib import admin

from .models import Listing, Bid, Comment, Watchlist, User, Category

# Register your models here.

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ('listings',)

class ListingAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'active']
    ordering = ['category', 'name']

admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(User)
admin.site.register(Category)
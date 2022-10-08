from django.contrib import admin
from .models import Route, Event, Place, Review


class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'route_name', 'route_type', 'country', 'location', 'duration')
    list_display_links = ('id', 'route_name')
    search_fields = 'route_name',


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'start_date')
    list_display_links = ('id', 'route')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'route_id')
    list_display_links = ('id', 'route_id')


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


admin.site.register(Route, RouteAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Place, PlaceAdmin)
admin.site.register(Review, ReviewAdmin)

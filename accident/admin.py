from django.contrib import admin

from accident.models import Accident, AccidentСategory, DangerType, DangerEvent, DangerCategory


@admin.register(AccidentСategory)
class AccidentСategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_per_page = 15


@admin.register(Accident)
class AccidentAdmin(admin.ModelAdmin):
    list_display = ('date', 'order', 'organization', 'category', 'is_death')
    search_fields = ('order', 'organization', 'danger__event_description', 'danger__code')
    autocomplete_fields = ['danger']
    list_per_page = 15


@admin.register(DangerCategory)
class DangerCategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')
    search_fields = ('name', 'order')
    list_per_page = 15


@admin.register(DangerType)
class DangerTypeAdmin(admin.ModelAdmin):
    list_display = ('order', 'category', 'description')
    search_fields = ('order', 'category__name', 'description')
    autocomplete_fields = ['category']
    list_per_page = 15


@admin.register(DangerEvent)
class DangerEventAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'event_description')
    search_fields = ('code', 'type__description', 'event_description')
    autocomplete_fields = ['type']
    list_per_page = 15

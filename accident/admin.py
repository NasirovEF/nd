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
    search_fields = ('order', 'organization')
    list_per_page = 15


@admin.register(DangerCategory)
class DangerCategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')
    search_fields = ('name',)
    list_per_page = 15


@admin.register(DangerType)
class DangerCategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'category', 'description')
    search_fields = ('category', 'description')
    list_per_page = 15


@admin.register(DangerEvent)
class DangerEventAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'event_description')
    search_fields = ('code', 'type', 'event_description')
    list_per_page = 15

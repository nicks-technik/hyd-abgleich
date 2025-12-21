from django.contrib import admin
from .models import HeatingSystem, Room, Radiator

class RadiatorInline(admin.TabularInline):
    model = Radiator
    extra = 1

class RoomInline(admin.StackedInline):
    model = Room
    extra = 1

@admin.register(HeatingSystem)
class HeatingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'supply_temperature', 'return_temperature', 'created_at')
    inlines = [RoomInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'area_sqm', 'target_temp')
    list_filter = ('system',)
    inlines = [RadiatorInline]

@admin.register(Radiator)
class RadiatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'room', 'radiator_type', 'width_mm', 'height_mm')
    list_filter = ('room__system', 'radiator_type')
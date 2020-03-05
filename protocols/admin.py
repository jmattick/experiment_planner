from django.contrib import admin

from .models import Event, Feature, Protocol, Step


class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Title', {'fields': ['title']}),
        ('Start', {'fields': ['start_time']})
    ]


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


class StepInline(admin.TabularInline):
    model = Step
    extra = 3


class ProtocolAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields': ['name']}),
        ('Days',    {'fields': ['days']}),
        ('Description', {'fields': ['description']})
    ]
    inlines = [StepInline]
    list_display = ('name', 'description', 'days')
    search_fields = ['name']


admin.site.register(Protocol, ProtocolAdmin)
admin.site.register(Event, EventAdmin)

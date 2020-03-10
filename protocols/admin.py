from django.contrib import admin

from .models import Event, Feature, Protocol, Step


# class EventAdmin(admin.ModelAdmin):
#     fieldsets = [
#         ('Title', {'fields': ['title']}),
#         ('Start', {'fields': ['start_time']}),
#         ('Minutes', {'fields': ['minutes']})
#     ]

class EventInline(admin.TabularInline):
    model = Event
    extra = 1


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


class StepAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Type', {'fields': ['type']}),
        ('Description', {'fields': ['step_text']}),
        ('Time', {'fields': ['time_min']})
    ]
    inlines = [EventInline]
    list_display = ('get_protocol', 'type', 'step_text', 'time_min')

    def get_protocol(self, obj):
        return obj.protocol.name
    get_protocol.admin_order_field = 'protocol'
    get_protocol.short_description = 'Protocol'


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
admin.site.register(Step, StepAdmin)

from django.contrib import admin

from station.models import Bus, Facility, Trip, Ticket, Order


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Bus)
admin.site.register(Facility)
admin.site.register(Trip)
admin.site.register(Ticket)


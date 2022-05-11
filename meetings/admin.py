from django.contrib import admin
from .models import Meeting, Dashboard

class DashboardInline(admin.TabularInline):
    model = Dashboard


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('uid', 'owner', 'team')
    inlines = [DashboardInline]


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'view_meeting_team')

    @admin.display(empty_value="??")
    def view_meeting_team(self, obj):
        return obj.meeting.team

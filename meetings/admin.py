from django.contrib import admin
from .models import Meeting, Dashboard, MeetingDetail, SharedUser



@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('uid', 'owner', 'team')


@admin.register(SharedUser)
class SharedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'meeting')

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'view_meeting_team')
    
    @admin.display(empty_value="??")
    def view_meeting_team(self, obj):
        return obj.meeting.team


@admin.register(MeetingDetail)
class MeetingDetailAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'view_meeting_team')
    
    @admin.display(empty_value="??")
    def view_meeting_team(self, obj):
        return obj.meeting.team
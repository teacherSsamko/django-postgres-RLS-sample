from django.contrib import admin
from .models import Meeting, Dashboard

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('uid', 'owner', 'team')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('meeting', )

from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from rules.contrib.views import PermissionRequiredMixin


from .models import Meeting, Dashboard, MeetingDetail, Role


class MeetingListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view for a list of meetings."""
    model = Meeting
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        team = user.groups.first()
        role = Role.objects.filter(user=user) # hit
        if role and role.first().user_role == Role.Roles.ADMIN.value:
            return Meeting.objects.filter(team=team)
        else:
            return Meeting.objects.filter(owner=user)


class MeetingDetailView(PermissionRequiredMixin, generic.DetailView):
    """Generic class-based detail view for a dashboard."""
    model = Meeting
    permission_required = 'meetings.read_meeting_detail'

class MeetingDetailListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based list view for a list of meeting details."""
    model = MeetingDetail
    paginate_by = 10

    def get_queryset(self):
        team = self.request.user.groups.first()
        return MeetingDetail.objects.filter(meeting__team=team)


class DashboardListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based list view for a list of dashboards."""
    model = Dashboard
    paginate_by = 10

    def get_queryset(self):
        team = self.request.user.groups.first()
        return Dashboard.objects.filter(meeting__team=team)

class DashboardDetailView(PermissionRequiredMixin, generic.DetailView):
    """Generic class-based detail view for a dashboard."""
    model = Dashboard
    permission_required = 'meetings.read_dashboard_detail'


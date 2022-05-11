from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from rules.contrib.views import PermissionRequiredMixin


from .models import Meeting, Dashboard


class MeetingListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view for a list of meetings."""
    model = Meeting
    paginate_by = 10


class DashboardListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based list view for a list of dashboards."""
    model = Dashboard
    paginate_by = 10

class DashboardDetailView(PermissionRequiredMixin, generic.DetailView):
    """Generic class-based detail view for a dashboard."""
    model = Dashboard
    permission_required = 'meetings.read_dashboard'


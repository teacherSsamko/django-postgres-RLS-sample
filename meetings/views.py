from importlib import import_module

from django.shortcuts import get_object_or_404, render, HttpResponse
from django.views import generic, View
from django.db.models import Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from rules.contrib.views import PermissionRequiredMixin

from .models import Meeting, Dashboard, MeetingDetail, Role, SharedLink


class MeetingListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view for a list of meetings."""
    model = Meeting
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        team = user.groups.first()
        role = Role.objects.filter(user=user, team=team)
        print(f"role: {role}")
        print("user_role: ", role.first().user_role)
        if role and role.first().user_role == Role.Roles.ADMIN.value:
            # members = team.user_set.all()
            return Meeting.objects.filter(owner__in=team.user_set.all())
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


def proxy_link(request, uid):
    link: SharedLink = SharedLink.objects.get(uid=uid)
    if not link.is_active: return HttpResponse("inactive link")
    shared_with = link.shared_with

    def _is_accessible(user: User, shared_with: int):
        if user == "not accessible": return False # TODO: fix it
        return True

    if not _is_accessible(request.user, shared_with):
        return HttpResponse("you're not accessible")

    role = link.role

    def _give_permission(user: User, role: int):
        # TODO: give permission by role
        return

    _give_permission(request.user, role)
    
    target, id = link.target.split("#") # 'meetings.models.Meeting#1'
    module_path, class_name = target.rsplit(".", 1)
    module = import_module(module_path)
    klass = getattr(module, class_name)

    result = get_object_or_404(klass, id=id)

    # TODO: redirect to target page or return its url
    return HttpResponse(result)

class SharedLinkView(View):
    def post(self, request):
        # update SharedLink
        return

    def get(self, request, uid):
        # proxy link to target
        link: SharedLink = SharedLink.objects.get(uid=uid)
        if not link.is_active: return HttpResponse("inactive link")
        shared_with = link.shared_with
        if not self._is_accessible(request.user, shared_with):
            return HttpResponse("you're not accessible")

        role = link.role
        self._give_permission(request.user, role)
        
        target_instance = self._get_target_instance(link.target)

        # TODO: redirect to target page or return its url
        return HttpResponse(target_instance)

    def _is_accessible(self, user: User, shared_with: int):
        if user == "not accessible": return False # TODO: fix it using shared_with
        return True

    def _give_permission(self, user: User, role: int):
        return

    def _get_target_instance(self, target: str):
        target_model, id = target.split("#") # 'meetings.models.Meeting#1'
        module_path, class_name = target_model.rsplit(".", 1)
        module = import_module(module_path)
        klass = getattr(module, class_name)

        return get_object_or_404(klass, id=id)    
    
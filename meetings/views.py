
import inspect
from importlib import import_module

from django.shortcuts import get_object_or_404, HttpResponse, redirect
from django.urls import reverse
from django.views import generic, View
from django.db import connection
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rules.contrib.views import PermissionRequiredMixin

from .models import Meeting, Dashboard, MeetingDetail, Role, SharedLink, ShareRole


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


# def proxy_link(request, uid):
#     link: SharedLink = SharedLink.objects.get(uid=uid)
#     if not link.is_active: return HttpResponse("inactive link")
#     shared_with = link.shared_with

#     def _is_accessible(user: User, shared_with: int):
#         if user == "not accessible": return False # TODO: fix it
#         return True

#     if not _is_accessible(request.user, shared_with):
#         return HttpResponse("you're not accessible")

#     role = link.role

#     def _give_permission(user: User, role: int):
#         # TODO: give permission by role
#         return

#     _give_permission(request.user, role)
    
#     target, id = link.target.split("#") # 'meetings.models.Meeting#1'
#     module_path, class_name = target.rsplit(".", 1)
#     module = import_module(module_path)
#     klass = getattr(module, class_name)

#     result = get_object_or_404(klass, id=id)

#     # TODO: redirect to target page or return its url
    
#     return redirect(to=reverse("my-meetings-detail", pk=id))

class SharedLinkView(View):
    def post(self, request):
        
        target_model = request.data.pop("target_model") # 'Meeting'
        pk = request.data.pop("pk")
        
        SharedLink.objects.create(
            target=self._get_target(target_model, pk),
            owner=request.user,
            **request.data
        )
        return

    def get(self, request, uid):
        # proxy link to target
        link: SharedLink = SharedLink.objects.get(uid=uid)
        self.restricted = False
        self._import_target_module(link)

        if not link.is_active: return HttpResponse("inactive link")
        if not self._is_accessible(request.user, link):
            return HttpResponse("you're not accessible")

        role = link.role
        self._give_permission(request.user, role)
        
        target_instance = self._get_target_instance()

        url_name = f"{self.model_str.lower()}-detail" # It needs url_map or strict url_rule
        return redirect(to=reverse(url_name, kwargs={"pk": self.target_id}))

    def _get_target(target_model_str:str, id: int):
        target_model = globals().get(target_model_str)
        model_path = inspect.getfile(target_model) # `/meetings/models.py`
        model_dotted_path = model_path.lstrip("/").rstrip(".py").replace("/", ".") # meetings.models
        return f"{model_dotted_path}.{target_model}#{id}"

    def _import_target_module(self, link:SharedLink):
        target_model, self.target_id = link.target.split("#") # 'meetings.models.Meeting#1'
        module_path, self.model_str = target_model.rsplit(".", 1)
        self.module = import_module(module_path)

    def _is_accessible(self, user: User, link: SharedLink):
        shared_with = link.shared_with
        if shared_with == SharedLink.SharedWith.ANYONE.value:
            return True
        elif shared_with == SharedLink.SharedWith.TEAM.value:
            if self._check_in_same_group(user, link.owner): return True
        elif shared_with == SharedLink.SharedWith.RESTRICTED.value:
            self.restricted = True
            if self._check_invitation(user): return True

        return False

    def _give_permission(self, user: User, role: int):
        if self.restricted:
            # Follow Access table's role
            pass
        else:
            with connection.cursor() as db:
                if role == ShareRole.VIEWER.value:
                    db.execute("SET ROLE viewer")
                elif role == ShareRole.COMMENTER.value:
                    db.execute("SET ROLE commenter")
                elif role == ShareRole.EDITOR.value:
                    db.execute("SET ROLE editor")
                else:
                    raise Exception("Invalid Role")
            print("DB role changed")
        

    def _get_target_instance(self):
        klass = getattr(self.module, self.model_str)

        return get_object_or_404(klass, id=self.target_id)    
    
    def _find_all_groups_of(self, user: User) -> set:
        return set(user.groups.values_list('name', flat=True))

    def _check_in_same_group(self, a: User, b: User) -> bool:
        same_groups = self._find_all_groups_of(a).intersection(self._find_all_groups_of(b))
        return True if same_groups else False

    def _check_invitation(self, user: User):
        print("in _check_invitation", user)
        access_table = getattr(self.module, f"{self.model_str}Invitee") # not use
        # access_table = getattr(self.module, f"{self.model_str}Access") # use this
        print(access_table)
        groups = user.groups.values_list('id', flat=True)
        print("groups:", groups)
        if access_table.objects.filter(
            Q(shared_user=user) | 
            Q(shared_group__in=groups)
        ).exists():
            return True


        return False
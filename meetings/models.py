import os
from math import ceil
from base64 import urlsafe_b64encode

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group

from rules.contrib.models import RulesModel



class ShareRole(models.IntegerChoices):
        VIEWER = 1, 'Viewer'
        COMMENTER = 2, 'Commenter'
        EDITOR = 3, 'Editor'


class Role(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Group, on_delete=models.CASCADE)
    class Roles(models.IntegerChoices):
        ADMIN = 1, "Admin"
        MEMBER = 2, "Member"
        
    user_role = models.PositiveSmallIntegerField(choices=Roles.choices, default=Roles.MEMBER)


class Meeting(RulesModel):
    uid = models.CharField(
        unique=True, default=urlsafe_b64encode(
        os.urandom(ceil(12 * 6 / 8))).rstrip(b'=').decode('ascii'), max_length=40, db_index=True)
    owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)


class SharedUser(RulesModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class MeetingDetail(RulesModel):
    # MeetingDetail has one version for the team. 
    # All team member can access to it
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE)
    data = models.TextField()


class Dashboard(RulesModel):
    # Dashboard has different version by each team member
    # each member can see only one's own dashboard on list view
    # but, all members can access to other's dashboard via shared link
    meeting = models.ForeignKey(Meeting, models.CASCADE)
    contents = models.TextField(default="Default Dashboard Text")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class MeetingInvitee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    shared_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    shared_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ShareRole.choices, default=ShareRole.VIEWER)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="only_one_of_user_or_group",
                check=(
                    Q(shared_user__isnull=True, shared_group__isnull=False) | 
                    Q(shared_user__isnull=False, shared_group__isnull=True)
                )
            ),
        ]


class SharedLink(models.Model):
    uid = models.CharField(
        unique=True, default=urlsafe_b64encode(
        os.urandom(ceil(12 * 6 / 8))).rstrip(b'=').decode('ascii'), max_length=40, db_index=True)
    target = models.CharField(max_length=512)

    class SharedWith(models.IntegerChoices):
        RESTRICTED = 1, 'Restricted' # Invitees only
        TEAM = 2, 'Team' # Share with one's team
        ANYOWN = 3, 'Anyone'

    shared_with = models.PositiveSmallIntegerField(choices=SharedWith.choices, default=SharedWith.RESTRICTED)
    role = models.PositiveSmallIntegerField(choices=ShareRole.choices, default=ShareRole.VIEWER)
    is_active = models.BooleanField(default=True)

    @property
    def url(self):
        return self.uid
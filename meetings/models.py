import os
from math import ceil
from base64 import urlsafe_b64encode

from django.db import models
from django.contrib.auth.models import User, Group


class Meeting(models.Model):
    uid = models.CharField(
        unique=True, default=urlsafe_b64encode(
        os.urandom(ceil(12 * 6 / 8))).rstrip(b'=').decode('ascii'), max_length=40, db_index=True)
    owner = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    # Who is the owner? Is the person who created the meeting the owner of it?
    team = models.ForeignKey(Group, models.SET_NULL, blank=True, null=True)
    # A user can be in multiple teams? or we could get the team from owner


class Dashboard(models.Model):
    meeting = models.ForeignKey(Meeting, models.CASCADE)
    contents = models.TextField(default="Default Dashboard Text")


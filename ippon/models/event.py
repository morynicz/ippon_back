import datetime

import pytz
from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    icon = models.ImageField(blank=True, null=True)
    banner = models.ImageField(blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)

    registration_start_time = models.DateTimeField()
    registration_end_time = models.DateTimeField()

    locationID = models.CharField(max_length=300, null=True)

    @property
    def registration_is_open(self) -> bool:
        now = datetime.datetime.now()
        if self.registration_start_time.replace(tzinfo=pytz.UTC) < now.replace(
                tzinfo=pytz.UTC) < self.registration_end_time.replace(tzinfo=pytz.UTC):
            return True
        else:
            return False

    @property
    def has_started(self) -> bool:
        now = datetime.datetime.now()
        if self.start_time.replace(tzinfo=pytz.UTC) < now.replace(tzinfo=pytz.UTC) < self.end_time.replace(
                tzinfo=pytz.UTC):
            return True
        else:
            return False


class EventAdmin(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

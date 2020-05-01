from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=100, blank=False)
    group_phase = models.ForeignKey('GroupPhase', related_name='groups', on_delete=models.PROTECT)


class GroupMember(models.Model):
    group = models.ForeignKey('Group', related_name='group_members', on_delete=models.PROTECT)
    team = models.ForeignKey('Team', related_name='group_member', on_delete=models.PROTECT)
from django.db import models


class GroupFight(models.Model):
    group = models.ForeignKey("Group", related_name="group_fights", on_delete=models.PROTECT)
    team_fight = models.ForeignKey("TeamFight", related_name="group_fight", on_delete=models.CASCADE)

    def __str__(self):
        return "group: {}\nteam_fight: {}".format(self.group, self.team_fight)

    def delete(self, using=None, keep_parents=False):
        super(GroupFight, self).delete()
        self.team_fight.delete()

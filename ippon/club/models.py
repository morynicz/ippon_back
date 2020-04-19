from django.db import models


class Club(models.Model):
    name = models.CharField(max_length=100, blank=False)
    webpage = models.URLField()
    description = models.TextField()
    city = models.CharField(max_length=100, blank=False)


class ClubAdmin(models.Model):
    club = models.ForeignKey('Club', related_name='admins', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='clubs', on_delete=models.PROTECT)

    def get_user(self):
        return {'id': self.user.id, 'username': self.user.username}
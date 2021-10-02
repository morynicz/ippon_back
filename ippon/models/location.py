from django.db import models


class Location(models.Model):
    tournament = models.ForeignKey(
        "Tournament", related_name="locations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100, blank=False)

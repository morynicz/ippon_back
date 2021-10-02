from django.db import models

SEX_CHOICES = [(0, "Male"), (1, "Female")]
RANK_CHOICES = [
    (0, "None"),
    (1, "Kyu_6"),
    (2, "Kyu_5"),
    (3, "Kyu_4"),
    (4, "Kyu_3"),
    (5, "Kyu_2"),
    (6, "Kyu_1"),
    (7, "Dan_1"),
    (8, "Dan_2"),
    (9, "Dan_3"),
    (10, "Dan_4"),
    (11, "Dan_5"),
    (12, "Dan_6"),
    (13, "Dan_7"),
    (14, "Dan_8"),
]


class Player(models.Model):
    sex = models.IntegerField(choices=SEX_CHOICES)
    rank = models.IntegerField(choices=RANK_CHOICES)
    name = models.CharField(max_length=100, blank=False)
    surname = models.CharField(max_length=100, blank=False)
    birthday = models.DateField()
    club_id = models.ForeignKey(
        "Club", related_name="players", on_delete=models.PROTECT
    )

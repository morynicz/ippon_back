import datetime
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase

import ippon.models.club as cl
import ippon.models.player as plm
import ippon.models.tournament as tm


class AuthorizationViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username="a1", password="password1")
        self.u2 = User.objects.create(username="a2", password="password2")
        self.u3 = User.objects.create(username="u3", password="password1")

        self.c1 = cl.Club.objects.create(name="cn1", webpage="http://cw1.co", description="cd1", city="cc1")
        self.c2 = cl.Club.objects.create(name="cn2", webpage="http://cw2.co", description="cd2", city="cc2")
        self.c4 = cl.Club.objects.create(name="cn4", webpage="http://cw4.co", description="cd4", city="cc4")
        self.a1 = cl.ClubAdmin.objects.create(user=self.u1, club=self.c1)
        self.a2 = cl.ClubAdmin.objects.create(user=self.u2, club=self.c2)
        self.p1 = plm.Player.objects.create(
            name="pn1",
            surname="ps1",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c1,
        )
        self.p2 = plm.Player.objects.create(
            name="pn2",
            surname="ps2",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c2,
        )
        self.p3 = plm.Player.objects.create(
            name="pn3",
            surname="ps3",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c1,
        )
        self.p4 = plm.Player.objects.create(
            name="pn4",
            surname="ps4",
            rank=7,
            birthday=datetime.date(year=2001, month=1, day=1),
            sex=1,
            club_id=self.c4,
        )
        self.valid_payload = {
            "name": "cn3",
            "webpage": "http://cw1.co",
            "description": "cd1",
            "city": "cc1",
        }

        self.tournament = tm.Tournament.objects.create(
            name="T1",
            webpage="http://w1.co",
            description="d1",
            city="c1",
            date=datetime.date(year=2021, month=1, day=1),
            address="a1",
            team_size=1,
            group_match_length=3,
            ko_match_length=3,
            final_match_length=3,
            finals_depth=0,
            age_constraint=5,
            age_constraint_value=20,
            rank_constraint=5,
            rank_constraint_value=7,
            sex_constraint=1,
        )


class AuthorizationViewsAuthenticatedTests(AuthorizationViewsTest):
    def setUp(self):
        super(AuthorizationViewsAuthenticatedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)


class AuthorizationViewsUnauthenticatedTests(AuthorizationViewsTest):
    def setUp(self):
        super(AuthorizationViewsUnauthenticatedTests, self).setUp()

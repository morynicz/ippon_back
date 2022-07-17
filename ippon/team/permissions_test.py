import datetime
import django.test
import unittest
from django.contrib.auth.models import User

import ippon.models.tournament as tm
import ippon.team.permissions as tep


class IsTeamOwnerTests(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create(username="admin", password="password")
        self.to = tm.Tournament.objects.create(
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
        self.team = self.to.teams.create(name="a")
        self.request = unittest.mock.Mock()
        self.view = unittest.mock.Mock()
        self.view.kwargs = dict()
        self.request.user = self.user
        self.permission = tep.IsTeamOwner()


class IsTeamOwnerAdminTests(IsTeamOwnerTests):
    def setUp(self):
        super(IsTeamOwnerAdminTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)
        self.view.kwargs = dict(pk=self.team.pk)

    def test_does_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.team)
        self.assertEqual(result, True)

    def test_does_permit_general(self):
        self.request.method = "PUT"
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, True)


class IsTeamOwnerNotAdminTests(IsTeamOwnerTests):
    def setUp(self):
        super(IsTeamOwnerNotAdminTests, self).setUp()

    def test_doesnt_permit_when_unsafe_method(self):
        self.request.method = "PUT"
        result = self.permission.has_object_permission(self.request, self.view, self.team)
        self.assertEqual(result, False)

    def test_doesnt_permit_general(self):
        result = self.permission.has_permission(self.request, self.view)
        self.assertEqual(result, False)

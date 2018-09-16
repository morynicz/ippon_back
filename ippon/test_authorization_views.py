import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club, ClubAdmin, Tournament, TournamentAdmin, TeamFight, Team, Fight


class AuthorizationViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.u1 = User.objects.create(username='a1', password='password1')
        self.u2 = User.objects.create(username='a2', password='password2')
        self.u3 = User.objects.create(username='u3', password='password1')

        self.c1 = Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.c2 = Club.objects.create(name='cn2', webpage='http://cw2.co', description='cd2', city='cc2')
        self.c4 = Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        self.a1 = ClubAdmin.objects.create(user=self.u1, club=self.c1)
        self.a2 = ClubAdmin.objects.create(user=self.u1, club=self.c2)
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p4 = Player.objects.create(name='pn4', surname='ps4', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c4)
        self.valid_payload = {
            "name": "cn3",
            "webpage": "http://cw1.co",
            "description": "cd1",
            "city": "cc1"
        }


class AuthorizationViewsSetAuthenticatedTests(AuthorizationViewsTest):
    def setUp(self):
        super(AuthorizationViewsSetAuthenticatedTests, self).setUp()
        self.client.force_authenticate(user=self.u1)


class ClubAuthorizationAuthenticatedTests(AuthorizationViewsSetAuthenticatedTests):
    def setUp(self):
        super(ClubAuthorizationAuthenticatedTests, self).setUp()
        self.c1 = Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')

    def test_club_authorization_returns_positive_auth_if_authorized(self):
        ClubAdmin.objects.create(user=self.u1, club=self.c1)
        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.c1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_club_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.c1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentAuthorizationAuthenticatedTests(AuthorizationViewsSetAuthenticatedTests):
    def setUp(self):
        super(TournamentAuthorizationAuthenticatedTests, self).setUp()
        self.tournament = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                    date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                    team_size=1, group_match_length=3, ko_match_length=3,
                                                    final_match_length=3, finals_depth=0, age_constraint=5,
                                                    age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                    sex_constraint=1)

    def test_tournament_admin_authorization_returns_positive_auth_if_authorized(self):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=True)

        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.id}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_positive_auth_if_authorized(self):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=False)

        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.id}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_admin_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_fight_authorization_returns_negative_auth_if_not_authorized(self):
        club = Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('fight-authorization', kwargs={'pk': fight.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_fight_authorization_returns_positive_auth_if_authorized(self):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=False)
        club = Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
        expected = {
            "isAuthorized": True
        }

        response = self.client.get(reverse('fight-authorization', kwargs={'pk': fight.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthorizationViewsSetUnauthenticatedTests(AuthorizationViewsTest):
    def setUp(self):
        super(AuthorizationViewsSetUnauthenticatedTests, self).setUp()


class ClubAuthorizationUnauthenticatedTests(AuthorizationViewsSetUnauthenticatedTests):
    def setUp(self):
        super(ClubAuthorizationUnauthenticatedTests, self).setUp()
        self.club = Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')

    def test_club_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('club-authorization', kwargs={'pk': self.club.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentAuthorizationUnauthenticatedTests(AuthorizationViewsSetUnauthenticatedTests):
    def setUp(self):
        super(TournamentAuthorizationUnauthenticatedTests, self).setUp()
        self.tournament = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                    date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                    team_size=1, group_match_length=3, ko_match_length=3,
                                                    final_match_length=3, finals_depth=0, age_constraint=5,
                                                    age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                    sex_constraint=1)

    def test_tournament_admin_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_staff_authorization_returns_negative_auth_if_not_authenticated(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.tournament.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_fight_authorization_returns_negative_auth(self):
        club = Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('fight-authorization', kwargs={'pk': fight.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


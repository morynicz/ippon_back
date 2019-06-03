import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club, ClubAdmin, TournamentAdmin, TeamFight, Team, Fight, GroupPhase, Tournament, \
    CupPhase


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
        self.a2 = ClubAdmin.objects.create(user=self.u2, club=self.c2)
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c1)
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.c2)
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


class TournamentAuthorizationAuthenticatedTests(AuthorizationViewsSetAuthenticatedTests):
    def setUp(self):
        super(TournamentAuthorizationAuthenticatedTests, self).setUp()
        self.tournament = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                    date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                    team_size=1, group_match_length=3, ko_match_length=3,
                                                    final_match_length=3, finals_depth=0, age_constraint=5,
                                                    age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                    sex_constraint=1)


class TournamentAdminAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentAdminAuthenticatedTests, self).setUp()

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


class TournamentFightAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentFightAuthorizationAuthenticatedTests, self).setUp()

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

    def test_tournament_fight_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_fight_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_fight_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_fight_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_fight_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
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


class TournamentTeamFightAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentTeamFightAuthorizationAuthenticatedTests, self).setUp()

    def test_tournament_team_fight_authorization_returns_negative_auth_if_not_authorized(self):
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('team-fight-authorization', kwargs={'pk': tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_team_fight_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_team_fight_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_team_fight_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_team_fight_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_team_fight_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('team-fight-authorization', kwargs={'pk': tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentTeamAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentTeamAuthorizationAuthenticatedTests, self).setUp()

    def test_tournament_team_authorization_returns_negative_auth_if_not_authorized(self):
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('team-authorization', kwargs={'pk': t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_team_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_team_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_team_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_team_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_team_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('team-authorization', kwargs={'pk': t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentGroupAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentGroupAuthorizationAuthenticatedTests, self).setUp()
        self.group_phase = GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)

    def test_tournament_group_authorization_returns_negative_auth_if_not_authorized(self):
        g1 = self.group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_group_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_group_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_group_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_group_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        g1 = self.group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentGroupPhaseAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentGroupPhaseAuthorizationAuthenticatedTests, self).setUp()
        self.group_phase = GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)

    def test_tournament_group_phase_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': self.group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_phase_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_group_phase_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_group_phase_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_group_phase_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_group_phase_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': self.group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TournamentCupPhaseAuthorizationAuthenticatedTests(TournamentAuthorizationAuthenticatedTests):
    def setUp(self):
        super(TournamentCupPhaseAuthorizationAuthenticatedTests, self).setUp()
        self.cup_phase = CupPhase.objects.create(name="cp1", tournament=self.tournament, fight_length=3, final_fight_length=5)

    def test_tournament_cup_phase_authorization_returns_negative_auth_if_not_authorized(self):
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('cup-phase-authorization', kwargs={'pk': self.cup_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_cup_phase_authorization_returns_positive_auth_if_authorized_staff(self):
        self.parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(False)

    def test_tournament_cup_phase_authorization_returns_positive_auth_if_authorized_admin(self):
        self.parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(True)

    def parametrized_cup_phase_authorization_returns_positive_auth_if_authorized(self, is_admin):
        TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('cup-phase-authorization', kwargs={'pk': self.cup_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuthorizationViewsSetUnauthenticatedTests(AuthorizationViewsTest):
    def setUp(self):
        super(AuthorizationViewsSetUnauthenticatedTests, self).setUp()


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

    def test_tournament_team_fight_authorization_returns_negative_auth(self):
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        t2 = Team.objects.create(name="t2", tournament=self.tournament)
        tf = TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('team-fight-authorization', kwargs={'pk': tf.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_authorization_returns_negative_auth(self):
        group_phase = GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)
        g1 = group_phase.groups.create(name="g1")
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-authorization', kwargs={'pk': g1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_team_authorization_returns_negative_auth(self):
        t1 = Team.objects.create(name="t1", tournament=self.tournament)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('team-authorization', kwargs={'pk': t1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_group_phase_authorization_returns_negative_auth_if_not_authorized(self):
        group_phase = GroupPhase.objects.create(name="gp1", tournament=self.tournament, fight_length=3)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('group-phase-authorization', kwargs={'pk': group_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tournament_cup_phase_authorization_returns_negative_auth_if_not_authorized(self):
        cup_phase = CupPhase.objects.create(name="cp1", tournament=self.tournament, fight_length=3, final_fight_length=5)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('cup-phase-authorization', kwargs={'pk': cup_phase.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

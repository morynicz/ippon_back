import datetime

from django.urls.base import reverse
from rest_framework import status

import ippon.models
from ippon.utils.authorization_test_fixtures import AuthorizationViewsAuthenticatedTests, AuthorizationViewsUnauthenticatedTests
from ippon.models import club as cl, team as tem, team_fight as tfm, player as plm, tournament as tm


class TournamentFightAuthorizationAuthenticatedTests(AuthorizationViewsAuthenticatedTests):
    def setUp(self):
        super(TournamentFightAuthorizationAuthenticatedTests, self).setUp()

    def test_tournament_fight_authorization_returns_negative_auth_if_not_authorized(self):
        club = cl.Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = ippon.models.fight.Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
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
        tm.TournamentAdmin.objects.create(user=self.u1, tournament=self.tournament, is_master=is_admin)
        club = cl.Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = ippon.models.fight.Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
        expected = {
            "isAuthorized": True
        }
        response = self.client.get(reverse('fight-authorization', kwargs={'pk': fight.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class FightViewsUnauthenticatedTests(AuthorizationViewsUnauthenticatedTests):
    def setUp(self):
        super(FightViewsUnauthenticatedTests, self).setUp()

    def test_tournament_fight_authorization_returns_negative_auth(self):
        club = cl.Club.objects.create(name='cn4', webpage='http://cw4.co', description='cd4', city='cc4')
        t1 = tem.Team.objects.create(name="t1", tournament=self.tournament)
        t2 = tem.Team.objects.create(name="t2", tournament=self.tournament)
        tf = tfm.TeamFight.objects.create(tournament=self.tournament, aka_team=t1, shiro_team=t2)
        p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=club)
        fight = ippon.models.fight.Fight.objects.create(team_fight=tf, aka=p1, shiro=p2)
        expected = {
            "isAuthorized": False
        }

        response = self.client.get(reverse('fight-authorization', kwargs={'pk': fight.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
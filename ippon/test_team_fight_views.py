import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club, Team, TournamentAdmin, TeamFight
from ippon.tournament.tournament import Tournament

BAD_PK = 0


class TeamFightViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        c = Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.admin = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)
        self.t1 = Team.objects.create(tournament=self.to, name='t1')
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t1.team_members.create(player=self.p1)
        self.t2 = Team.objects.create(tournament=self.to, name='t2')
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.team_members.create(player=self.p2)

        self.t3 = Team.objects.create(tournament=self.to, name='t3')
        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t3.team_members.create(player=self.p3)
        self.t4 = Team.objects.create(tournament=self.to, name='t4')
        self.p4 = Player.objects.create(name='pn4', surname='ps4', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t4.team_members.create(player=self.p4)

        self.tf1 = TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.tf2 = TeamFight.objects.create(aka_team=self.t3, shiro_team=self.t4, tournament=self.to)

        self.tf1_json = {'id': self.tf1.id, 'aka_team': self.t1.id, 'shiro_team': self.t2.id, 'tournament': self.to.id}
        self.tf2_json = {'id': self.tf2.id, 'aka_team': self.t3.id, 'shiro_team': self.t4.id, 'tournament': self.to.id}
        self.valid_payload = {'id': self.tf1.id, 'aka_team': self.t1.id, 'shiro_team': self.t1.id,
                              'tournament': self.to.id}
        self.invalid_payload = {'id': self.tf1.id, 'aka_team': self.t1.id, 'shiro_team': BAD_PK,
                                'tournament': self.to.id}


class TeamFightViewSetAuthorizedTests(TeamFightViewTest):
    def setUp(self):
        super(TeamFightViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_post_valid_payload_creates_specified_team_fight(self):
        response = self.client.post(
            reverse('teamfight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('teamfight-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_team_fight(self):
        response = self.client.put(
            reverse('teamfight-detail', kwargs={'pk': self.tf1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.tf1_json.copy()
        expected['shiro_team'] = self.valid_payload['shiro_team']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('teamfight-detail', kwargs={'pk': self.tf1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_team_fight_deletes_it(self):
        response = self.client.delete(reverse('teamfight-detail', kwargs={'pk': self.tf1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_team_fight_returns_bad_request(self):
        response = self.client.delete(reverse('teamfight-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TeamFightViewSetUnauthorizedTests(TeamFightViewTest):
    def setUp(self):
        super(TeamFightViewSetUnauthorizedTests, self).setUp()

    def test_list_returns_all_fights(self):
        response = self.client.get(reverse('teamfight-list'))

        self.assertEqual([self.tf1_json, self.tf2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_fight_returns_correct_fight(self):
        response = self.client.get(reverse('teamfight-detail', kwargs={'pk': self.tf1.pk}))
        self.assertEqual(self.tf1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_fight_returns_404(self):
        response = self.client.get(reverse('teamfight-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('teamfight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('teamfight-detail', kwargs={'pk': self.tf1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UnauthorizedTeamFightsFightsTest(TeamFightViewSetUnauthorizedTests):
    def setUp(self):
        super(UnauthorizedTeamFightsFightsTest, self).setUp()
        self.f1 = self.tf1.fights.create(aka=self.p1, shiro=self.p2)
        self.f2 = self.tf1.fights.create(aka=self.p2, shiro=self.p1)

        self.f1_json = {'id': self.f1.id, 'aka': self.p1.id, 'shiro': self.p2.id, 'team_fight': self.tf1.id}
        self.f2_json = {'id': self.f2.id, 'aka': self.p2.id, 'shiro': self.p1.id, 'team_fight': self.tf1.id}

    def test_get_fights_for_valid_team_fight_returns_list_of_fights(self):
        expected = [self.f1_json, self.f2_json]
        response = self.client.get(reverse('teamfight-fights', kwargs={'pk': self.tf1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fights_for_invalid_team_fight_returns_not_found(self):
        response = self.client.get(reverse('teamfight-fights', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

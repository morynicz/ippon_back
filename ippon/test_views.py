import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt import authentication

from ippon.models import Player, Club, Tournament, Team, TournamentAdmin


class TeamsViewTest(TestCase):
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
        self.t1.members.create(player=self.p1)
        self.t2 = Team.objects.create(tournament=self.to, name='t2')
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.members.create(player=self.p2)
        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.members.create(player=self.p3)
        self.t1_json = {'id': self.t1.id, 'tournament': self.to.id, 'members': [self.p1.id], 'name': 't1'}
        self.t2_json = {'id': self.t2.id, 'tournament': self.to.id, 'members': [self.p2.id, self.p3.id], 'name': 't2'}
        self.valid_payload = {'tournament': self.to.id, 'name': 't3'}
        self.invalid_payload = {'tournament': self.to.id, 'name': ''}


class TeamViewSetAuthorizedTests(TeamsViewTest):
    def setUp(self):
        super(TeamViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_teams_post_valid_payload_creates_specified_team(self):
        response = self.client.post(
            reverse('team-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teams_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('team-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teams_put_valid_payload_updates_team(self):
        response = self.client.put(
            reverse('team-detail', kwargs={'pk': self.t1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.t1_json.copy()
        expected['name'] = self.valid_payload['name']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teams_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('team-detail', kwargs={'pk': self.t1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teams_delete_existing_team_deletes_it(self):
        response = self.client.delete(reverse('team-detail', kwargs={'pk': self.t1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_teams_delete_not_existing_team_returns_bad_request(self):
        response = self.client.delete(reverse('team-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TeamViewSetUnauthorizedTests(TeamsViewTest):
    def setUp(self):
        super(TeamViewSetUnauthorizedTests, self).setUp()

    def test_teams_list_returns_all_teams(self):
        response = self.client.get(reverse('team-list'))
        teams = Team.objects.all()

        self.assertEqual([self.t1_json, self.t2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teams_detail_for_existing_team_returns_correct_team(self):
        response = self.client.get(reverse('team-detail', kwargs={'pk': self.t1.pk}))
        self.assertEqual(self.t1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teams_detail_for_not_existing_team_returns_404(self):
        response = self.client.get(reverse('team-detail', kwargs={'pk': -1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('team-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

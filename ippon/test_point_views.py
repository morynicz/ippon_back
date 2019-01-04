import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club, Team, TournamentAdmin, TeamFight, Tournament

BAD_PK = 0

class PointsViewTest(APITestCase):
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

        self.tf = TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.f = self.tf.fights.create(aka=self.p1, shiro=self.p2)

        self.po1 = self.f.points.create(player=self.p1, type=0)
        self.po2 = self.f.points.create(player=self.p2, type=1)

        self.po1_json = {'id': self.po1.id, 'player': self.p1.id, 'fight': self.f.id, 'type': 0}
        self.po2_json = {'id': self.po2.id, 'player': self.p2.id, 'fight': self.f.id, 'type': 1}
        self.valid_payload = {'player': self.p1.id, 'fight': self.f.id, 'type': 3}
        self.invalid_payload = {'player': self.p1.id, 'fight': self.f.id, 'type': 7}


class PointViewSetAuthorizedTests(PointsViewTest):
    def setUp(self):
        super(PointViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_post_valid_payload_creates_specified_point(self):
        response = self.client.post(
            reverse('point-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('point-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_point(self):
        response = self.client.put(
            reverse('point-detail', kwargs={'pk': self.po1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.po1_json.copy()
        expected['type'] = self.valid_payload['type']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('point-detail', kwargs={'pk': self.po1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_point_deletes_it(self):
        response = self.client.delete(reverse('point-detail', kwargs={'pk': self.po1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_point_returns_bad_request(self):
        response = self.client.delete(reverse('point-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PointViewSetUnauthorizedTests(PointsViewTest):
    def setUp(self):
        super(PointViewSetUnauthorizedTests, self).setUp()

    def test_list_returns_all_points(self):
        response = self.client.get(reverse('point-list'))

        self.assertEqual([self.po1_json, self.po2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_point_returns_correct_point(self):
        response = self.client.get(reverse('point-detail', kwargs={'pk': self.po1.pk}))
        self.assertEqual(self.po1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_point_returns_404(self):
        response = self.client.get(reverse('point-detail', kwargs={'pk': -1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('point-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('point-detail', kwargs={'pk': self.po1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

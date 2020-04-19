import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Team, TeamFight
import ippon.tournament.models as tm
import ippon.player.models as plm
import ippon.club.models as cl

BAD_PK = 0


class FightViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        c = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')
        self.user = User.objects.create(username='admin', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        self.t1 = Team.objects.create(tournament=self.to, name='t1')
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t1.team_members.create(player=self.p1)
        self.t2 = Team.objects.create(tournament=self.to, name='t2')
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.team_members.create(player=self.p2)

        self.tf = TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.f1 = self.tf.fights.create(aka=self.p1, shiro=self.p2)
        self.f2 = self.tf.fights.create(aka=self.p2, shiro=self.p1)

        self.f1_json = {'id': self.f1.id, 'aka': self.p1.id, 'shiro': self.p2.id, 'team_fight': self.tf.id, 'status': 0,
                        'winner': 0}
        self.f2_json = {'id': self.f2.id, 'aka': self.p2.id, 'shiro': self.p1.id, 'team_fight': self.tf.id, 'status': 0,
                        'winner': 0}
        self.valid_payload = {'id': self.f1.id, 'aka': self.p1.id, 'shiro': self.p1.id, 'team_fight': self.tf.id,
                              'status': 1, 'winner': 0}
        self.invalid_payload = {'id': self.f1.id, 'aka': self.p1.id, 'shiro': BAD_PK, 'team_fight': self.tf.id,
                                'status': 0, 'winner': 0}


class FightViewSetAuthorizedTests(FightViewTest):
    def setUp(self):
        super(FightViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)

    def test_post_valid_payload_creates_specified_fight(self):
        response = self.client.post(
            reverse('fight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('fight-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_fight(self):
        response = self.client.put(
            reverse('fight-detail', kwargs={'pk': self.f1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.f1_json.copy()
        expected['shiro'] = self.valid_payload['shiro']
        expected['status'] = self.valid_payload['status']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('fight-detail', kwargs={'pk': self.f1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_fight_deletes_it(self):
        response = self.client.delete(reverse('fight-detail', kwargs={'pk': self.f1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_fight_returns_bad_request(self):
        response = self.client.delete(reverse('fight-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FightViewSetUnauthenticatedTests(FightViewTest):
    def setUp(self):
        super(FightViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_fights(self):
        response = self.client.get(reverse('fight-list'))

        self.assertEqual([self.f1_json, self.f2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_fight_returns_correct_fight(self):
        response = self.client.get(reverse('fight-detail', kwargs={'pk': self.f1.pk}))
        self.assertEqual(self.f1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_fight_returns_404(self):
        response = self.client.get(reverse('fight-detail', kwargs={'pk': -1}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FightViewSetUnauthorizedTests(FightViewTest):
    def setUp(self):
        super(FightViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_unauthorized_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('fight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('fight-detail', kwargs={'pk': self.f1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('fight-detail', kwargs={'pk': self.t1.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UnauthenticatedFightsPointsTest(FightViewSetUnauthenticatedTests):
    def setUp(self):
        super(UnauthenticatedFightsPointsTest, self).setUp()
        self.po1 = self.f1.points.create(player=self.p1, type=0)
        self.po2 = self.f1.points.create(player=self.p2, type=1)
        self.po3 = self.f2.points.create(player=self.p2, type=1)

        self.po1_json = {'id': self.po1.id, 'player': self.p1.id, 'fight': self.f1.id, 'type': 0}
        self.po2_json = {'id': self.po2.id, 'player': self.p2.id, 'fight': self.f1.id, 'type': 1}

    def test_get_points_for_valid_fight_returns_list_of_fights_points(self):
        expected = [self.po1_json, self.po2_json]
        response = self.client.get(reverse('fight-points', kwargs={'pk': self.f1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_points_for_invalid_fight_returns_list_of_fights_points(self):
        response = self.client.get(reverse('fight-points', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

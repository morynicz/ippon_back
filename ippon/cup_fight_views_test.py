import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import TeamFight, CupFight
import ippon.team.models as tem
import ippon.tournament.models as tm
import ippon.player.models as plm
import ippon.club.models as cl
from ippon.utils import BAD_PK


class CupFightViewTest(APITestCase):
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
        self.t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t1.team_members.create(player=self.p1)
        self.t2 = tem.Team.objects.create(tournament=self.to, name='t2')
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t2.team_members.create(player=self.p2)

        self.t3 = tem.Team.objects.create(tournament=self.to, name='t3')
        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t3.team_members.create(player=self.p3)
        self.t4 = tem.Team.objects.create(tournament=self.to, name='t4')
        self.p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.t4.team_members.create(player=self.p4)

        self.tf1 = TeamFight.objects.create(aka_team=self.t1, shiro_team=self.t2, tournament=self.to)
        self.tf2 = TeamFight.objects.create(aka_team=self.t3, shiro_team=self.t4, tournament=self.to)

        self.phase = self.to.cup_phases.create(name='phase', fight_length=3, final_fight_length=4)

        self.cf1 = self.phase.cup_fights.create(team_fight=self.tf1)
        self.cf2 = self.phase.cup_fights.create(team_fight=self.tf2, previous_aka_fight=self.cf1)
        self.cf3 = self.phase.cup_fights.create(previous_aka_fight=self.cf2)

        self.cf1_json = {'id': self.cf1.id, 'team_fight': self.tf1.id, 'cup_phase': self.phase.id,
                         "previous_aka_fight": None, "previous_shiro_fight": None}
        self.cf2_json = {'id': self.cf2.id, 'team_fight': self.tf2.id, 'cup_phase': self.phase.id,
                         "previous_aka_fight": self.cf1.id, "previous_shiro_fight": None}
        self.cf3_json = {'id': self.cf3.id, 'team_fight': None, 'cup_phase': self.phase.id,
                         "previous_aka_fight": self.cf2.id, "previous_shiro_fight": None}
        self.valid_payload = {'id': self.cf1.id, 'team_fight': self.tf2.id, 'cup_phase': self.phase.id,
                              "previous_aka_fight": None, "previous_shiro_fight": None}
        self.invalid_payload = {'id': self.cf1.id, 'group': BAD_PK}


class CupFightViewSetAuthorizedTests(CupFightViewTest):
    def setUp(self):
        super(CupFightViewSetAuthorizedTests, self).setUp()
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to, is_master=False)
        self.client.force_authenticate(user=self.user)

    def test_post_valid_payload_creates_specified_cup_fight(self):
        response = self.client.post(
            reverse('cupfight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('cupfight-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_cup_fight(self):
        response = self.client.put(
            reverse('cupfight-detail', kwargs={'pk': self.cf1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.cf1_json.copy()
        expected['team_fight'] = self.valid_payload['team_fight']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('cupfight-detail', kwargs={'pk': self.cf1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_cup_fight_deletes_it(self):
        response = self.client.delete(reverse('cupfight-detail', kwargs={'pk': self.cf1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CupFight.DoesNotExist):
            CupFight.objects.get(pk=self.cf1.id)
        with self.assertRaises(TeamFight.DoesNotExist):
            TeamFight.objects.get(pk=self.cf1.team_fight.id)

    def test_delete_existing_cup_fight_without_teamfight_deletes_it(self):
        response = self.client.delete(reverse('cupfight-detail', kwargs={'pk': self.cf3.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(CupFight.DoesNotExist):
            CupFight.objects.get(pk=self.cf3.id)

    def test_delete_not_existing_cup_fight_returns_bad_request(self):
        response = self.client.delete(reverse('cupfight-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CupFightViewSetUnauthenticatedTests(CupFightViewTest):
    def setUp(self):
        super(CupFightViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_fights(self):
        response = self.client.get(reverse('cupfight-list'))
        self.assertEqual([self.cf1_json, self.cf2_json, self.cf3_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_fight_returns_correct_fight(self):
        response = self.client.get(reverse('cupfight-detail', kwargs={'pk': self.cf1.pk}))
        self.assertEqual(self.cf1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_fight_returns_404(self):
        response = self.client.get(reverse('cupfight-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('cupfight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_gets_unauthorized(self):
        response = self.client.put(
            reverse('cupfight-detail', kwargs={'pk': self.cf1.id}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('cupfight-detail', kwargs={'pk': self.cf1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CupFightViewSetUnauthorizedTests(CupFightViewTest):
    def setUp(self):
        super(CupFightViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_post_gets_forbidden(self):
        response = self.client.post(
            reverse('cupfight-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_gets_forbidden(self):
        response = self.client.put(
            reverse('cupfight-detail', kwargs={'pk': self.cf1.id}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_gets_forbidden(self):
        response = self.client.delete(reverse('cupfight-detail', kwargs={'pk': self.cf1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.utils import json

import ippon.team_fight.models as tfm
import ippon.team.models as tem
import ippon.tournament.models as tm
import ippon.player.models as plm
import ippon.club.models as cl
from ippon.utils import BAD_PK


class GroupViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(username='admin', password='password')
        self.not_admin = User.objects.create(username='user', password='password')
        self.to = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                               date=datetime.date(year=2021, month=1, day=1), address='a1',
                                               team_size=1, group_match_length=3, ko_match_length=3,
                                               final_match_length=3, finals_depth=0, age_constraint=5,
                                               age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                               sex_constraint=1)
        tm.TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)
        self.group_phase = self.to.group_phases.create(fight_length=3)
        self.group1 = self.group_phase.groups.create(name='G1')
        self.group2 = self.group_phase.groups.create(name='G2')
        self.group1_json = {'id': self.group1.id, "name": "G1", "group_phase": self.group_phase.id}
        self.group2_json = {'id': self.group2.id, "name": "G2", "group_phase": self.group_phase.id}
        self.valid_payload = {'id': self.group1.id, "name": "G4", "group_phase": self.group_phase.id}
        self.invalid_payload = {'id': self.group1.id, "name": "", "group_phase": self.group_phase.id}


class GroupViewSetAuthorizedTests(GroupViewTest):
    def setUp(self):
        super(GroupViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_post_valid_payload_creates_specified_group(self):
        response = self.client.post(
            reverse('group-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('group-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_group(self):
        response = self.client.put(
            reverse('group-detail', kwargs={'pk': self.group1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.group1_json.copy()
        expected['name'] = self.valid_payload['name']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('group-detail', kwargs={'pk': self.group1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_group_deletes_it(self):
        response = self.client.delete(reverse('group-detail', kwargs={'pk': self.group1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_group_returns_bad_request(self):
        response = self.client.delete(reverse('group-detail', kwargs={'pk': -5}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupViewSetUnauthorizedTests(GroupViewTest):
    def setUp(self):
        super(GroupViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.not_admin)

    def test_put_gets_forbidden(self):
        response = self.client.put(
            reverse('group-detail', kwargs={'pk': self.group1.id}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_gets_forbidden(self):
        response = self.client.post(
            reverse('group-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_gets_forbidden(self):
        response = self.client.delete(reverse('group-detail', kwargs={'pk': self.group1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GroupViewSetUnauthenticatedTests(GroupViewTest):
    def setUp(self):
        super(GroupViewSetUnauthenticatedTests, self).setUp()

    def test_list_returns_all_fights(self):
        response = self.client.get(reverse('group-list'))

        self.assertEqual([self.group1_json, self.group2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_fight_returns_correct_fight(self):
        response = self.client.get(reverse('group-detail', kwargs={'pk': self.group1.pk}))
        self.assertEqual(self.group1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_fight_returns_404(self):
        response = self.client.get(reverse('group-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('group-detail', kwargs={'pk': self.group1.id}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('group-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('group-detail', kwargs={'pk': self.group1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_group_fights_for_valid_group_returns_list_of_fights(self):
        t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        t2 = tem.Team.objects.create(tournament=self.to, name='t2')
        t3 = tem.Team.objects.create(tournament=self.to, name='t3')

        self.group1.group_members.create(team=t1)
        self.group1.group_members.create(team=t2)
        self.group1.group_members.create(team=t3)

        tf1 = tfm.TeamFight.objects.create(aka_team=t1, shiro_team=t2, tournament=self.to)
        tf2 = tfm.TeamFight.objects.create(aka_team=t1, shiro_team=t2, tournament=self.to)

        gf1 = self.group1.group_fights.create(team_fight=tf1)
        gf2 = self.group1.group_fights.create(team_fight=tf2)

        gf1_json = {
            'team_fight': tf1.id,
            'group': self.group1.id,
            'id': gf1.id
        }

        gf2_json = {
            'team_fight': tf2.id,
            'group': self.group1.id,
            'id': gf2.id
        }

        expected = [gf1_json, gf2_json]
        response = self.client.get(reverse('group-group_fights', kwargs={'pk': self.group1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_fights_for_invalid_group_returns_not_found(self):
        response = self.client.get(reverse('group-group_fights', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupViewSetMembersTests(GroupViewTest):
    def setUp(self):
        super(GroupViewSetMembersTests, self).setUp()
        self.t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        self.t2 = tem.Team.objects.create(tournament=self.to, name='t2')
        self.t3 = tem.Team.objects.create(tournament=self.to, name='t3')
        self.t4 = tem.Team.objects.create(tournament=self.to, name='t4')

        self.group1.group_members.create(team=self.t1)
        self.group1.group_members.create(team=self.t2)


class GroupViewSetMembersUnauthorizedTests(GroupViewSetMembersTests):
    def setUp(self):
        super(GroupViewSetMembersUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.not_admin)

    def test_get_members_returns_list_of_members(self):
        response = self.client.get(reverse('group-members', kwargs={'pk': self.group1.pk}))

        expected = [{'id': self.t1.id, 'tournament': self.to.id, 'members': [], 'name': 't1'},
                    {'id': self.t2.id, 'tournament': self.to.id, 'members': [], 'name': 't2'}]
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_members_returns_forbidden(self):
        response = self.client.get(reverse('group-not-assigned', kwargs={'pk': self.group1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GroupViewSetMembersUnauthenticatedTests(GroupViewSetMembersTests):
    def setUp(self):
        super(GroupViewSetMembersUnauthenticatedTests, self).setUp()

    def test_get_members_returns_list_of_members(self):
        response = self.client.get(reverse('group-members', kwargs={'pk': self.group1.pk}))

        expected = [{'id': self.t1.id, 'tournament': self.to.id, 'members': [], 'name': 't1'},
                    {'id': self.t2.id, 'tournament': self.to.id, 'members': [], 'name': 't2'}]
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_members_returns_unauthorized(self):
        response = self.client.get(reverse('group-not-assigned', kwargs={'pk': self.group1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupMemberViewSetScoreCountingTests(GroupViewTest):
    def setUp(self):
        super(GroupMemberViewSetScoreCountingTests, self).setUp()
        c = cl.Club.objects.create(
            name='cn1',
            webpage='http://cw1.co',
            description='cd1',
            city='cc1')

        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p5 = plm.Player.objects.create(name='pn5', surname='ps5', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)
        self.p6 = plm.Player.objects.create(name='pn6', surname='ps6', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=c)

        self.t1 = tem.Team.objects.create(tournament=self.to, name='t1')
        self.t2 = tem.Team.objects.create(tournament=self.to, name='t2')
        self.t3 = tem.Team.objects.create(tournament=self.to, name='t3')

        self.group1.group_members.create(team=self.t1)
        self.group1.group_members.create(team=self.t2)
        self.group1.group_members.create(team=self.t3)

        self.t1.team_members.create(player=self.p1)
        self.t1.team_members.create(player=self.p2)
        self.t2.team_members.create(player=self.p3)
        self.t2.team_members.create(player=self.p4)
        self.t3.team_members.create(player=self.p5)
        self.t3.team_members.create(player=self.p6)

        tf1 = self.to.team_fights.create(aka_team=self.t1, shiro_team=self.t2)
        tf2 = self.to.team_fights.create(aka_team=self.t1, shiro_team=self.t3)
        tf3 = self.to.team_fights.create(aka_team=self.t2, shiro_team=self.t3)

        self.group1.group_fights.create(team_fight=tf1)
        self.group1.group_fights.create(team_fight=tf2)
        self.group1.group_fights.create(team_fight=tf3)

        f1 = tf1.fights.create(aka=self.p1, shiro=self.p3)
        f1.points.create(player=self.p1, type=0)
        f1.points.create(player=self.p3, type=1)
        f1.points.create(player=self.p1, type=2)
        f1.winner = 1
        f1.status = 2
        f1.save()

        f2 = tf1.fights.create(aka=self.p2, shiro=self.p4)
        f2.points.create(player=self.p4, type=3)
        f2.points.create(player=self.p2, type=1)
        f2.status = 2
        f2.save()

        tf1.status = 2
        tf1.winner = 1
        tf1.save()

        f3 = tf2.fights.create(aka=self.p1, shiro=self.p5)
        f3.points.create(player=self.p1, type=4)
        f3.points.create(player=self.p1, type=4)
        f3.points.create(player=self.p5, type=5)
        f3.points.create(player=self.p1, type=1)
        f3.points.create(player=self.p1, type=1)
        f3.winner = 1
        f3.status = 2
        f3.save()

        f4 = tf2.fights.create(aka=self.p2, shiro=self.p6)
        f4.points.create(player=self.p2, type=1)
        f4.points.create(player=self.p2, type=1)
        f4.winner = 2
        f4.status = 2
        f4.save()

        tf2.status = 2
        tf2.save()

        f5 = tf3.fights.create(aka=self.p3, shiro=self.p5)
        f5.points.create(player=self.p3, type=2)
        f5.points.create(player=self.p3, type=2)
        f5.winner = 1
        f5.status = 2
        f5.save()

        f6 = tf3.fights.create(aka=self.p4, shiro=self.p6)
        f6.points.create(player=self.p6, type=3)
        f6.points.create(player=self.p6, type=3)
        f6.winner = 2
        f6.status = 2
        f6.save()

        tf3.status = 2
        tf3.save()

    def test_get_group_memeber_1_scores_returns_score(self):
        expected_response = {
            "wins": 1,
            "draws": 1,
            "points": 7,
            "id": self.t1.id
        }
        self.group_member_score_test(expected_response, self.t1.id)

    def group_member_score_test(self, expected_response, team_id):
        response = self.client.get(
            reverse('group-member_score', kwargs={'pk': self.group1.id, 'team_id': team_id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    def test_get_group_memeber_2_scores_returns_score(self):
        expected_response = {
            "wins": 0,
            "draws": 1,
            "points": 4,
            "id": self.t2.id
        }
        self.group_member_score_test(expected_response, self.t2.id)

    def test_get_group_memeber_3_scores_returns_score(self):
        expected_response = {
            "wins": 0,
            "draws": 2,
            "points": 3,
            "id": self.t3.id
        }
        self.group_member_score_test(expected_response, self.t3.id)


class AuthorizedGroupMembersViewTests(GroupViewSetMembersTests):
    def setUp(self):
        super(AuthorizedGroupMembersViewTests, self).setUp()
        self.client.force_authenticate(user=self.admin)


class ValidIdsGroupMembersViewTests(AuthorizedGroupMembersViewTests):
    def setUp(self):
        super(ValidIdsGroupMembersViewTests, self).setUp()

    def test_post_valid_payload_creates_specified_group_member(self):
        response = self.client.post(
            reverse('group-members', kwargs={'pk': self.group1.id, 'team_id': self.t1.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_existing_group_member_deletes_it(self):
        response = self.client.delete(reverse('group-members', kwargs={'pk': self.group1.pk, 'team_id': self.t2.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_groups_get_non_members_returns_list_of_participants_not_assigned_to_a_team(self):
        response = self.client.get(reverse('group-not-assigned', kwargs={'pk': self.group1.pk}))
        expected = [{'id': self.t3.id, 'tournament': self.to.id, 'members': [], 'name': 't3'},
                    {'id': self.t4.id, 'tournament': self.to.id, 'members': [], 'name': 't4'}]
        self.assertCountEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InvalidIdsGroupMemberViewTests(AuthorizedGroupMembersViewTests):
    def setUp(self):
        super(InvalidIdsGroupMemberViewTests, self).setUp()

    def test_groups_post_invalid_group_member_returns_forbidden(self):
        t3 = tem.Team.objects.create(tournament=self.to, name='t3')

        response = self.client.post(
            reverse('group-members', kwargs={'pk': BAD_PK, 'team_id': t3.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_groups_post_invalid_groups_returns_404(self):
        g3 = self.group_phase.groups.create(name='G3')
        response = self.client.post(
            reverse('group-members', kwargs={'pk': g3.id, 'team_id': BAD_PK}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_not_existing_group_member_returns_bad_request(self):
        t3 = tem.Team.objects.create(tournament=self.to, name='t3')
        response = self.client.delete(reverse('group-members', kwargs={'pk': self.group1.id, 'team_id': t3.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_groups_get_non_members_returns_forbidden(self):
        response = self.client.get(reverse('group-not-assigned', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

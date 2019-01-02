import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.utils import json

from ippon.models import TournamentAdmin, Team, TeamFight
from ippon.tournament.tournament import Tournament

BAD_PK = 0


class GroupViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create(username='admin', password='password')
        self.to = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                            date=datetime.date(year=2021, month=1, day=1), address='a1',
                                            team_size=1, group_match_length=3, ko_match_length=3,
                                            final_match_length=3, finals_depth=0, age_constraint=5,
                                            age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                            sex_constraint=1)
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to, is_master=False)
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

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('group-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('group-detail', kwargs={'pk': self.group1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_group_fights_for_valid_group_returns_list_of_fights(self):
        t1 = Team.objects.create(tournament=self.to, name='t1')
        t2 = Team.objects.create(tournament=self.to, name='t2')
        t3 = Team.objects.create(tournament=self.to, name='t3')

        self.group1.group_members.create(team=t1)
        self.group1.group_members.create(team=t2)
        self.group1.group_members.create(team=t3)

        tf1=TeamFight.objects.create(aka_team=t1, shiro_team=t2, tournament=self.to)
        tf2=TeamFight.objects.create(aka_team=t1, shiro_team=t2, tournament=self.to)

        gf1=self.group1.group_fights.create(team_fight=tf1)
        gf2=self.group1.group_fights.create(team_fight=tf2)

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
        self.t1 = Team.objects.create(tournament=self.to, name='t1')
        self.t2 = Team.objects.create(tournament=self.to, name='t2')
        self.t3 = Team.objects.create(tournament=self.to, name='t3')
        self.t4 = Team.objects.create(tournament=self.to, name='t4')

        self.group1.group_members.create(team=self.t1)
        self.group1.group_members.create(team=self.t2)


class GroupViewSetMembersUnauthorizedTests(GroupViewSetMembersTests):
    def setUp(self):
        super(GroupViewSetMembersUnauthorizedTests, self).setUp()

    def test_groups_get_members_returns_list_of_members(self):
        response = self.client.get(reverse('group-members', kwargs={'pk': self.group1.pk}))

        expected = [{'id': self.t1.id, 'tournament': self.to.id, 'members': [], 'name': 't1'},
                    {'id': self.t2.id, 'tournament': self.to.id, 'members': [], 'name': 't2'}]
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teams_get_non_members_returns_unauthorized(self):
        response = self.client.get(reverse('team-not-assigned', kwargs={'pk': self.group1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_groups_post_invalid_group_returns_404(self):
        t3 = Team.objects.create(tournament=self.to, name='t3')

        response = self.client.post(
            reverse('group-members', kwargs={'pk': BAD_PK, 'team_id': t3.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_groups_post_invalid_groups_returns_404(self):
        g3 = self.group_phase.groups.create(name='G3')
        response = self.client.post(
            reverse('group-members', kwargs={'pk': g3.id, 'team_id': BAD_PK}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_not_existing_group_member_returns_bad_request(self):
        t3 = Team.objects.create(tournament=self.to, name='t3')
        response = self.client.delete(reverse('group-members', kwargs={'pk': self.group1.id, 'team_id': t3.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_groups_get_non_members_returns_404(self):
        response = self.client.get(reverse('group-not-assigned', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

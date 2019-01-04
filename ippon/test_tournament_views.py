import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ippon.models import Player, Club, Tournament, TournamentAdmin, Team

BAD_PK = 0


class TournamentViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.club = Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.admin = User.objects.create(username='admin', password='password')
        self.to1 = Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                             date=datetime.date(year=2021, month=1, day=1), address='a1',
                                             team_size=1, group_match_length=3, ko_match_length=3,
                                             final_match_length=3, finals_depth=0, age_constraint=5,
                                             age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                             sex_constraint=1)
        self.to2 = Tournament.objects.create(name='T2', webpage='http://w2.co', description='d2', city='c2',
                                             date=datetime.date(year=2022, month=2, day=2), address='a2',
                                             team_size=2, group_match_length=3, ko_match_length=3,
                                             final_match_length=3, finals_depth=0, age_constraint=5,
                                             age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                             sex_constraint=1)
        self.adm1 = TournamentAdmin.objects.create(user=self.admin, tournament=self.to1, is_master=True)
        TournamentAdmin.objects.create(user=self.admin, tournament=self.to2, is_master=True)

        self.to1_json = {
            'id': self.to1.id,
            "name": 'T1',
            "webpage": 'http://w1.co',
            "description": 'd1',
            "city": 'c1',
            "date": "2021-01-01",
            "address": 'a1',
            "team_size": 1,
            "group_match_length": 3,
            "ko_match_length": 3,
            "final_match_length": 3,
            "finals_depth": 0,
            "age_constraint": 5,
            "age_constraint_value": 20,
            "rank_constraint": 5,
            "rank_constraint_value": 7,
            "sex_constraint": 1
        }
        self.to2_json = {
            'id': self.to2.id,
            "name": 'T2',
            "webpage": 'http://w2.co',
            "description": 'd2',
            "city": 'c2',
            "date": "2022-02-02",
            "address": 'a2',
            "team_size": 2,
            "group_match_length": 3,
            "ko_match_length": 3,
            "final_match_length": 3,
            "finals_depth": 0,
            "age_constraint": 5,
            "age_constraint_value": 20,
            "rank_constraint": 5,
            "rank_constraint_value": 7,
            "sex_constraint": 1
        }
        self.valid_payload = {
            'id': self.to1.id,
            "name": 'T11',
            "webpage": 'http://w1.co',
            "description": 'd1',
            "city": 'c1',
            "date": "2021-1-1",
            "address": 'a1',
            "team_size": 1,
            "group_match_length": 3,
            "ko_match_length": 3,
            "final_match_length": 3,
            "finals_depth": 0,
            "age_constraint": 5,
            "age_constraint_value": 20,
            "rank_constraint": 5,
            "rank_constraint_value": 7,
            "sex_constraint": 1
        }
        self.invalid_payload = {
            'id': self.to1.id,
            "name": 'T1',
            "webpage": 'http://w1.co',
            "description": 'd1',
            "city": 'c1',
            "date": "2021-1-1",
            "address": 'a1',
            "team_size": 1,
            "group_match_length": 3,
            "ko_match_length": 3,
            "final_match_length": 3,
            "finals_depth": 0,
            "age_constraint": 20,
            "age_constraint_value": 20,
            "rank_constraint": 5,
            "rank_constraint_value": 7,
            "sex_constraint": 3
        }


class TournamentViewSetAuthorizedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentViewSetAuthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_post_valid_payload_creates_specified_tournament(self):
        response = self.client.post(
            reverse('tournament-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_payload_returns_400(self):
        response = self.client.post(
            reverse('tournament-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_valid_payload_updates_tournament(self):
        response = self.client.put(
            reverse('tournament-detail', kwargs={'pk': self.to1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        expected = self.to1_json.copy()
        expected['name'] = self.valid_payload['name']
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_invalid_payload_gets_bad_request(self):
        response = self.client.put(
            reverse('tournament-detail', kwargs={'pk': self.to1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_existing_tournament_deletes_it(self):
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': self.to2.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_tournament_returns_bad_request(self):
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentViewSetUnauthorizedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentViewSetUnauthorizedTests, self).setUp()

    def test_list_returns_all_tournaments(self):
        response = self.client.get(reverse('tournament-list'))

        self.assertEqual([self.to1_json, self.to2_json], response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_existing_tournament_returns_correct_tournament(self):
        response = self.client.get(reverse('tournament-detail', kwargs={'pk': self.to1.pk}))
        self.assertEqual(self.to1_json, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_for_not_existing_tournament_returns_404(self):
        response = self.client.get(reverse('tournament-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.post(
            reverse('tournament-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_delete_gets_unauthorized(self):
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TournamentAdminTest(TournamentViewTest):
    def setUp(self):
        super(TournamentAdminTest, self).setUp()
        self.user2 = User.objects.create(username='user2', password='password')
        self.user3 = User.objects.create(username='user3', password='password')
        self.user4 = User.objects.create(username='user4', password='password')
        self.adm2 = TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)


class UnauthorizedTournamentAdminTest(TournamentAdminTest):
    def setUp(self):
        super(UnauthorizedTournamentAdminTest, self).setUp()

    def test_get_admins_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_non_admins_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-non-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTournamentAdminTest(TournamentAdminTest):
    def setUp(self):
        super(AuthorizedTournamentAdminTest, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_get_admins_for_valid_fight_returns_list_of_tournaments_admins(self):
        expected = [
            {
                'id': self.adm1.id,
                'is_master': True,
                'tournament_id': self.to1.id,
                'user': {
                    'id': self.admin.id,
                    'username': 'admin'
                }
            },
            {
                'id': self.adm2.id,
                'is_master': False,
                'tournament_id': self.to1.id,
                'user': {
                    'id': self.user2.id,
                    'username': 'user2'
                }
            }
        ]
        response = self.client.get(reverse('tournament-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_admins_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-admins', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_admins_for_valid_fight_returns_list_of_tournaments_non_admins(self):
        expected = [
            {
                'id': self.user3.id,
                'username': 'user3'
            },
            {
                'id': self.user4.id,
                'username': 'user4'
            }
        ]
        response = self.client.get(reverse('tournament-non-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_admins_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-non-admins', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentParticipantsTest(TournamentViewTest):
    def setUp(self):
        super(TournamentParticipantsTest, self).setUp()
        self.p1 = Player.objects.create(name='pn1', surname='ps1', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par1 = self.to1.participations.create(player=self.p1, is_qualified=True)
        self.p2 = Player.objects.create(name='pn2', surname='ps2', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par2 = self.to1.participations.create(player=self.p2)

        self.p3 = Player.objects.create(name='pn3', surname='ps3', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.p4 = Player.objects.create(name='pn4', surname='ps4', rank=7,
                                        birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)


class UnauthorizedParticipantsTest(TournamentParticipantsTest):
    def setUp(self):
        super(UnauthorizedParticipantsTest, self).setUp()

    def test_get_participants_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-participants', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_non_participants_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-non-participants', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_participations_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-participations', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedParticipantsTest(TournamentParticipantsTest):
    def setUp(self):
        super(AuthorizedParticipantsTest, self).setUp()
        self.client.force_authenticate(user=self.admin)

    def test_get_participants_for_valid_tournament_returns_list_of_participants(self):
        expected = [
            {
                'id': self.p1.id,
                'name': 'pn1',
                'surname': 'ps1',
                'rank': 7,
                'birthday': '2001-01-01',
                'sex': 1,
                'club_id': self.club.id
            }
        ]
        response = self.client.get(reverse('tournament-participants', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_participants_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-participants', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_participants_for_valid_tournament_returns_list_of_tournaments_non_participants(self):
        expected = [
            {
                'id': self.p3.id,
                'name': 'pn3',
                'surname': 'ps3',
                'rank': 7,
                'birthday': '2001-01-01',
                'sex': 1,
                'club_id': self.club.id
            },
            {
                'id': self.p4.id,
                'name': 'pn4',
                'surname': 'ps4',
                'rank': 7,
                'birthday': '2001-01-01',
                'sex': 1,
                'club_id': self.club.id
            }
        ]
        response = self.client.get(reverse('tournament-non-participants', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_non_participants_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-non-participants', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participations_for_valid_tournament_returns_list_of_participations(self):
        expected = [
            {
                "player": {
                    'id': self.p1.id,
                    'name': 'pn1',
                    'surname': 'ps1'
                },
                'id': self.par1.id,
                "is_paid": False,
                "is_registered": False,
                "is_qualified": True,
                "is_sex_ok": True,
                "is_age_ok": True,
                "is_rank_ok": True,
                "tournament_id": self.to1.id,
                "notes": ""
            },
            {
                "player": {
                    'id': self.p2.id,
                    'name': 'pn2',
                    'surname': 'ps2'
                },
                'id': self.par2.id,
                "is_paid": False,
                "is_registered": False,
                "is_qualified": False,
                "is_sex_ok": True,
                "is_age_ok": True,
                "is_rank_ok": True,
                "tournament_id": self.to1.id,
                "notes": ""
            }
        ]
        response = self.client.get(reverse('tournament-participations', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_participations_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-participations', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentTeamTests(TournamentViewTest):
    def setUp(self):
        super(TournamentTeamTests, self).setUp()
        self.t1 = Team.objects.create(tournament=self.to1, name='t1')
        self.t2 = Team.objects.create(tournament=self.to1, name='t2')
        self.t3 = Team.objects.create(tournament=self.to2, name='t3')

    def test_get_teams_returns_list_of_tournament_teams(self):
        expected = [
            {
                "id": self.t1.id,
                "name": "t1",
                "members": [],
                "tournament": self.to1.id
            },
            {
                "id": self.t2.id,
                "name": "t2",
                "members": [],
                "tournament": self.to1.id
            }
        ]
        response = self.client.get(reverse('tournament-teams', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_teams_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-teams', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentAdminAuthorizationsTest(TournamentViewTest):
    def setUp(self):
        super(TournamentAdminAuthorizationsTest, self).setUp()

    def test_admin_auth_admin_returns_200_and_isAuthorized_true(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": True}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_auth_staff_returns_200_and_isAuthorized_true(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": True}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_auth_admin_returns_200_and_isAuthorized_false(self):
        self.user2 = User.objects.create(username='user2', password='password')
        self.adm2 = TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": False}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_auth_staff_returns_200_and_isAuthorized_true(self):
        self.user2 = User.objects.create(username='user2', password='password')
        self.adm2 = TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": True}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_auth_admin_returns_200_and_isAuthorized_false(self):
        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": False}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_staff_admin_returns_200_and_isAuthorized_false(self):
        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": False}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TournamentGroupPhasesUnauthorizedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentGroupPhasesUnauthorizedTests, self).setUp()

    def test_get_group_phases_for_valid_tournament_returns_list_of_group_phases(self):
        gp1 = self.to1.group_phases.create(name="gp1", fight_length=2)
        gp2 = self.to1.group_phases.create(name="gp2", fight_length=3)

        gp1_json = {
            'tournament': self.to1.id,
            'name': gp1.name,
            'fight_length': 2,
            'id': gp1.id
        }

        gp2_json = {
            'tournament': self.to1.id,
            'name': gp2.name,
            'fight_length': 3,
            'id': gp2.id
        }

        expected = [gp1_json, gp2_json]
        response = self.client.get(reverse('tournament-group_phases', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_phases_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-group_phases', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentCupPhasesUnauthorizedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentCupPhasesUnauthorizedTests, self).setUp()

    def test_get_cup_phases_for_valid_tournament_returns_list_of_cup_phases(self):
        cp1 = self.to1.cup_phases.create(fight_length=3, name="cp1", final_fight_length=4)
        cp2 = self.to1.cup_phases.create(fight_length=5, name="cp2", final_fight_length=6)

        cp1_json = {
            'id': cp1.id,
            'tournament': self.to1.id,
            'fight_length': 3,
            'name': 'cp1',
            'final_fight_length': 4
        }
        cp2_json = {
            'id': cp2.id,
            'tournament': self.to1.id,
            'fight_length': 5,
            'name': 'cp2',
            'final_fight_length': 6
        }

        expected = [cp1_json, cp2_json]
        response = self.client.get(reverse('tournament-cup_phases', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_cup_phases_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-cup_phases', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

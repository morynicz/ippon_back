import datetime
import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import ippon.models.team as tem
import ippon.models.tournament as tm
import ippon.models.player as plm
import ippon.models.club as cl

BAD_PK = 0


class TournamentViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.club = cl.Club.objects.create(name='cn1', webpage='http://cw1.co', description='cd1', city='cc1')
        self.user = User.objects.create(username='admin', password='password')
        self.to1 = tm.Tournament.objects.create(name='T1', webpage='http://w1.co', description='d1', city='c1',
                                                date=datetime.date(year=2021, month=1, day=1), address='a1',
                                                team_size=1, group_match_length=3, ko_match_length=3,
                                                final_match_length=3, finals_depth=0, age_constraint=5,
                                                age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                sex_constraint=1)
        self.to2 = tm.Tournament.objects.create(name='T2', webpage='http://w2.co', description='d2', city='c2',
                                                date=datetime.date(year=2022, month=2, day=2), address='a2',
                                                team_size=2, group_match_length=3, ko_match_length=3,
                                                final_match_length=3, finals_depth=0, age_constraint=5,
                                                age_constraint_value=20, rank_constraint=5, rank_constraint_value=7,
                                                sex_constraint=1)

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
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user)

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
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_existing_tournament_returns_bad_request(self):
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentViewSetUnauthorizedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentViewSetUnauthorizedTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_post_valid_payload_creates_specified_tournament(self):
        response = self.client.post(
            reverse('tournament-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_gets_forbidden(self):
        response = self.client.put(
            reverse('tournament-detail', kwargs={'pk': self.to1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_gets_forbidden(self):
        response = self.client.delete(reverse('tournament-detail', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TournamentViewSetUnauthenticatedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentViewSetUnauthenticatedTests, self).setUp()

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

    def test_unauthorized_post_gets_unauthorized(self):
        response = self.client.post(
            reverse('tournament-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_put_gets_unauthorized(self):
        response = self.client.put(
            reverse('tournament-detail', kwargs={'pk': self.to1.pk}),
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
        self.adm2 = tm.TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)


class UnauthorizedTournamentAdminTest(TournamentAdminTest):
    def setUp(self):
        super(UnauthorizedTournamentAdminTest, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_get_admins_returns_forbidden(self):
        response = self.client.get(reverse('tournament-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_non_admins_returns_forbidden(self):
        response = self.client.get(reverse('tournament-non-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnauthenticatedTournamentAdminTest(TournamentAdminTest):
    def setUp(self):
        super(UnauthenticatedTournamentAdminTest, self).setUp()

    def test_get_admins_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_non_admins_returns_unauthorized(self):
        response = self.client.get(reverse('tournament-non-admins', kwargs={'pk': self.to1.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTournamentAdminTest(TournamentAdminTest):
    def setUp(self):
        super(AuthorizedTournamentAdminTest, self).setUp()
        self.adm1 = tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user)

    def test_get_admins_for_valid_fight_returns_list_of_tournaments_admins(self):
        expected = [
            {
                'id': self.adm2.id,
                'is_master': False,
                'tournament_id': self.to1.id,
                'user': {
                    'id': self.user2.id,
                    'username': 'user2'
                }
            },
            {
                'id': self.adm1.id,
                'is_master': True,
                'tournament_id': self.to1.id,
                'user': {
                    'id': self.user.id,
                    'username': 'admin'
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
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par1 = self.to1.participations.create(player=self.p1, is_qualified=True)
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par2 = self.to1.participations.create(player=self.p2)

        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)


class UnauthenticatedParticipantsTest(TournamentParticipantsTest):
    def setUp(self):
        super(UnauthenticatedParticipantsTest, self).setUp()

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
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user)

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
        self.t1 = tem.Team.objects.create(tournament=self.to1, name='t1')
        self.t2 = tem.Team.objects.create(tournament=self.to1, name='t2')
        self.t3 = tem.Team.objects.create(tournament=self.to2, name='t3')

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
        self.adm1 = tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)

    def test_admin_auth_admin_returns_200_and_isAuthorized_true(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": True}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_auth_staff_returns_200_and_isAuthorized_true(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-staff-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": True}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_auth_admin_returns_200_and_isAuthorized_false(self):
        self.user2 = User.objects.create(username='user2', password='password')
        self.adm2 = tm.TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('tournament-admin-authorization', kwargs={'pk': self.to1.pk}))
        self.assertEqual({"isAuthorized": False}, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_auth_staff_returns_200_and_isAuthorized_true(self):
        self.user2 = User.objects.create(username='user2', password='password')
        self.adm2 = tm.TournamentAdmin.objects.create(user=self.user2, tournament=self.to1, is_master=False)
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


class TournamentGroupPhasesUnauthenticatedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentGroupPhasesUnauthenticatedTests, self).setUp()

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


class TournamentCupPhasesUnauthenticatedTests(TournamentViewTest):
    def setUp(self):
        super(TournamentCupPhasesUnauthenticatedTests, self).setUp()

    def test_get_cup_phases_for_valid_tournament_returns_list_of_cup_phases(self):
        cp1 = self.to1.cup_phases.create(fight_length=3, name="cp1", final_fight_length=4, number_of_positions=16)
        cp2 = self.to1.cup_phases.create(fight_length=5, name="cp2", final_fight_length=6, number_of_positions=15)

        cp1_json = {
            'id': cp1.id,
            'tournament': self.to1.id,
            'fight_length': 3,
            'name': 'cp1',
            'final_fight_length': 4,
            'number_of_positions': 16
        }
        cp2_json = {
            'id': cp2.id,
            'tournament': self.to1.id,
            'fight_length': 5,
            'name': 'cp2',
            'final_fight_length': 6,
            'number_of_positions': 15
        }

        expected = [cp1_json, cp2_json]
        response = self.client.get(reverse('tournament-cup_phases', kwargs={'pk': self.to1.pk}))
        self.assertEqual(expected, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_cup_phases_for_invalid_tournament_returns_not_found(self):
        response = self.client.get(reverse('tournament-cup_phases', kwargs={'pk': BAD_PK}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TournamentUnassignedPlayersTests(TournamentViewTest):
    def setUp(self):
        super(TournamentUnassignedPlayersTests, self).setUp()
        self.t1 = tem.Team.objects.create(tournament=self.to1, name='t1')
        self.p1 = plm.Player.objects.create(name='pn1', surname='ps1', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par1 = self.to1.participations.create(player=self.p1, is_qualified=True)
        self.t1.team_members.create(player=self.p1)
        self.p2 = plm.Player.objects.create(name='pn2', surname='ps2', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par2 = self.to1.participations.create(player=self.p2, is_qualified=True)
        self.t1.team_members.create(player=self.p2)
        self.p3 = plm.Player.objects.create(name='pn3', surname='ps3', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par3 = self.to1.participations.create(player=self.p3, is_qualified=True)
        self.p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                            birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        self.par4 = self.to1.participations.create(player=self.p4, is_qualified=True)

    def test_calling_get_on_not_assigned_participants_when_not_authenticated_returns_unauthorised(self):
        response = self.client.get(reverse('tournament-not_assigned', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_calling_get_on_not_assigned_participants_when_not_authorized_returns_forbidden(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-not_assigned', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_calling_get_on_not_assigned_participants_when_admin_returns_list_of_unassigned(self):
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=False)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-not_assigned', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'id': self.p3.id,
                'name': 'pn3',
                'surname': 'ps3'
            },
            {
                'id': self.p4.id,
                'name': 'pn4',
                'surname': 'ps4'
            }])

    def test_calling_get_on_not_assigned_participants_when_owner_returns_list_of_unassigned(self):
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-not_assigned', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'id': self.p3.id,
                'name': 'pn3',
                'surname': 'ps3'
            },
            {
                'id': self.p4.id,
                'name': 'pn4',
                'surname': 'ps4'
            }])

    def test_calling_get_un_unassigned_participants_when_authorized_returns_only_qualified_players(self):
        tm.TournamentAdmin.objects.create(user=self.user, tournament=self.to1, is_master=False)
        p4 = plm.Player.objects.create(name='pn4', surname='ps4', rank=7,
                                       birthday=datetime.date(year=2001, month=1, day=1), sex=1, club_id=self.club)
        par5 = self.to1.participations.create(player=self.p4)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('tournament-not_assigned', kwargs={'pk': self.to1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [
            {
                'id': self.p3.id,
                'name': 'pn3',
                'surname': 'ps3'
            },
            {
                'id': self.p4.id,
                'name': 'pn4',
                'surname': 'ps4'
            }])

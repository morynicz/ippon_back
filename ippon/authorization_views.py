from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.models
import ippon.models.fight
import ippon.models.group as gm
import ippon.models.team_fight as tfm
import ippon.models.team as tem
import ippon.models.tournament as tm
import ippon.models.player as plm
import ippon.models.club as cl


# TODO cut this file into pieces

@api_view(['GET'])
def club_authorization(request, pk, format=None):
    return has_club_authorization(pk, request)


def has_club_authorization(club_id, request):
    try:
        admin = cl.ClubAdmin.objects.get(user=request.user.id, club=club_id)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except cl.ClubAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


@api_view(['GET'])
def tournament_staff_authorization(request, pk, format=None):
    return has_tournament_authorization([True, False], pk, request)


@api_view(['GET'])
def tournament_admin_authorization(request, pk, format=None):
    return has_tournament_authorization(True, pk, request)


def has_tournament_authorization(allowed_master_statuses, pk, request):
    try:
        if not isinstance(allowed_master_statuses, list):
            allowed_master_statuses = [allowed_master_statuses]
        admin = tm.TournamentAdmin.objects.get(
            user=request.user.id,
            tournament=pk,
            is_master__in=allowed_master_statuses)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except tm.TournamentAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


@api_view(['GET'])
def fight_authorization(request, pk, format=None):
    fight = ippon.models.fight.Fight.objects.get(pk=pk)
    return has_tournament_authorization([True, False], fight.team_fight.tournament.id, request)


@api_view(['GET'])
def team_fight_authorization(request, pk, format=None):
    team_fight = tfm.TeamFight.objects.get(pk=pk)
    return has_tournament_authorization([True, False], team_fight.tournament.id, request)


@api_view(['GET'])
def team_authorization(request, pk, format=None):
    team = get_object_or_404(tem.Team.objects.all(), pk=pk)
    return has_tournament_authorization([True, False], team.tournament.id, request)


@api_view(['GET'])
def group_authorization(request, pk, format=None):
    group = get_object_or_404(gm.Group.objects.all(), pk=pk)
    return has_tournament_authorization([True, False], group.group_phase.tournament.id, request)


@api_view(['GET'])
def player_authorization(request, pk, format=None):
    player = get_object_or_404(plm.Player.objects.all(), pk=pk)
    return has_club_authorization(player.club_id, request)

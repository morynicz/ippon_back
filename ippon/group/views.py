from django.db.models.query_utils import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import ippon.tournament.authorizations as ta
import ippon.models.group as gm
import ippon.models.group_fight as gfm
import ippon.models.team as tem
import ippon.models.team_fight as tfm
import ippon.models.point as ptm
import ippon.group.permissions as gp
import ippon.group_fight.serializers as gfs
import ippon.group.serializers as gs
import ippon.team.serializers as tes


class GroupViewSet(viewsets.ModelViewSet):
    queryset = gm.Group.objects.all()
    serializer_class = gs.GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          gp.IsGroupOwnerOrReadOnly)

    # TODO: check when will DRF finally release the multiple actions for single url improvement
    @action(
        methods=['post', 'delete'],
        detail=True,
        url_name='members',
        url_path='members/(?P<team_id>[0-9]+)',
        permission_classes=[gp.IsGroupOwner])
    def handle_members(self, request, pk=None, team_id=None):
        return {
            'post': self.create_member,
            'delete': self.delete_member
        }[request.method.lower()](request, pk, team_id)

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<team_id>[0-9]+)')
    def create_member(self, request, pk=None, team_id=None):
        try:
            team = tem.Team.objects.get(pk=team_id)
            group = gm.Group.objects.get(pk=pk)
            group.group_members.create(team=team)
            return Response(status=status.HTTP_201_CREATED)
        except gm.Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except tem.Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @action(
    #     methods=['delete'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<team_id>[0-9]+)')
    def delete_member(self, request, pk=None, team_id=None):
        try:
            group = gm.Group.objects.get(pk=pk)
            team = tem.Team.objects.get(pk=team_id)
            membership = gm.GroupMember.objects.filter(group=group, team=team)
            if membership:
                membership.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except (gm.Group.DoesNotExist, tem.Team.DoesNotExist, gm.GroupMember.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True)
    def members(self, request, pk=None):
        serializer = tes.TeamSerializer(tem.Team.objects.filter(group_member__group=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=[
                permissions.IsAuthenticated,
                gp.IsGroupOwner])
    def not_assigned(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = tes.TeamSerializer(
            tem.Team.objects.filter(tournament__group_phases__groups=pk)
                .exclude(group_member__group__group_phase__groups=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='group_fights')
    def group_fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = gfs.GroupFightSerializer(gfm.GroupFight.objects.filter(group=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='member_score',
        url_path='members/(?P<team_id>[0-9]+)/score'
    )
    def member_score(self, request, pk=None, team_id=None):
        group = get_object_or_404(self.queryset, pk=pk)
        team = get_object_or_404(tem.Team.objects.all(), pk=team_id)
        fights = (tfm.TeamFight.objects.filter(group_fight__group=pk, aka_team=team_id) \
                  | tfm.TeamFight.objects.filter(group_fight__group=pk, shiro_team=team_id)).filter(status=2)
        wins = (fights.filter(aka_team=team_id, winner=1) \
                | fights.filter(shiro_team=team_id, winner=2)).count()

        draws = fights.filter(winner=0, status=2).count()
        points = ptm.Point.objects.exclude(type=4) \
            .filter(fight__team_fight__group_fight__group=pk, fight__team_fight__status=2) \
            .filter(Q(fight__team_fight__aka_team=team_id) | Q(fight__team_fight__shiro_team=team_id)) \
            .filter(player__in=team.get_member_ids()).count()

        return Response({"wins": wins, "draws": draws, "points": points, "id": team.id})


@api_view(['GET'])
def group_authorization(request, pk, format=None):
    group = get_object_or_404(gm.Group.objects.all(), pk=pk)
    return ta.has_tournament_authorization([True, False], group.group_phase.tournament.id, request)

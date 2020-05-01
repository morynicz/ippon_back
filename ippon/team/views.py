from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

import ippon.player.serializers as pls
import ippon.models.player as plm
import ippon.models.team as tem
import ippon.team.permissions as tep
import ippon.team.serializers as tes
import ippon.tournament.permissions as tp


class TeamViewSet(viewsets.ModelViewSet):
    queryset = tem.Team.objects.all()
    serializer_class = tes.TeamSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          tp.IsTournamentAdminOrReadOnlyDependent)

    # TODO: check when will DRF finally release the multiple actions for single url improvement
    @action(
        methods=['post', 'delete'],
        detail=True,
        url_name='members',
        url_path='members/(?P<player_id>[0-9]+)',
        permission_classes=(permissions.IsAuthenticated,
                            tep.IsTeamOwner))
    def handle_members(self, request, pk=None, player_id=None):
        return {
            'post': self.create_member,
            'delete': self.delete_member
        }[request.method.lower()](request, pk, player_id)

    # @action(
    #     methods=['post'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<player_id>[0-9]+)')
    def create_member(self, request, pk=None, player_id=None):
        try:
            player = plm.Player.objects.get(pk=player_id)
            team = tem.Team.objects.get(pk=pk)
            team.team_members.create(player=player)
            return Response(status=status.HTTP_201_CREATED)
        except plm.Player.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except tem.Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @action(
    #     methods=['delete'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<player_id>[0-9]+)')
    def delete_member(self, request, pk=None, player_id=None):
        try:
            player = plm.Player.objects.get(pk=player_id)
            team = tem.Team.objects.get(pk=pk)
            membership = tem.TeamMember.objects.filter(player=player, team=team)
            membership.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (plm.Player.DoesNotExist, tem.Team.DoesNotExist, tem.TeamMember.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True)
    def members(self, request, pk=None):
        serializer = pls.PlayerSerializer(plm.Player.objects.filter(team_member__team=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        tp.IsTournamentAdminDependent])
    def not_assigned(self, request, pk=None):
        serializer = pls.PlayerSerializer(
            plm.Player.objects.filter(participations__tournament__teams=pk)
                .exclude(team_member__team__tournament__teams=pk), many=True)
        return Response(serializer.data)

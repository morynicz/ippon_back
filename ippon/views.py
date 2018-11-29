from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from ippon.models import *
from ippon.permissions import *
from ippon.serializers import *


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsClubAdminOrReadOnlyDependent)


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsClubAdminOrReadOnlyClub)

    def perform_create(self, serializer):
        club = serializer.save()
        ca = ClubAdmin(user=self.request.user, club=club)
        ca.save()

    @action(methods=['get'], detail=True)
    def players(self, request, pk=None):
        serializer = PlayerSerializer(Player.objects.filter(club_id=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def admins(self, request, pk=None):
        serializer = ClubAdminSerializer(ClubAdmin.objects.filter(club=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def non_admins(self, request, pk=None):
        serializer = MinimalUserSerializer(User.objects.exclude(clubs__club=pk), many=True)
        return Response(serializer.data)


@api_view(['GET'])
def club_authorization(request, pk, format=None):
    try:
        admin = ClubAdmin.objects.get(user=request.user.id, club=pk)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except ClubAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyTournament)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def participations(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentParticipationSerializer(TournamentParticipation.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def non_participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = PlayerSerializer(Player.objects.exclude(participations__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def participants(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = PlayerSerializer(
            Player.objects.filter(participations__tournament=pk, participations__is_qualified=True), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tournament = serializer.save()
        ta = TournamentAdmin(user=self.request.user, tournament=tournament, is_master=True)
        ta.save()

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TournamentAdminSerializer(TournamentAdmin.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentOwner])
    def non_admins(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = MinimalUserSerializer(User.objects.exclude(tournaments__tournament=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def teams(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TeamSerializer(
            Team.objects.filter(tournament=pk), many=True)
        return Response(serializer.data)


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
        admin = TournamentAdmin.objects.get(
            user=request.user.id,
            tournament=pk,
            is_master__in=allowed_master_statuses)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({
            'isAuthorized': is_admin
        })

    except TournamentAdmin.DoesNotExist:
        return Response({
            'isAuthorized': False
        })


@api_view(['GET'])
def fight_authorization(request, pk, format=None):
    fight = Fight.objects.get(pk=pk)
    return has_tournament_authorization([True, False], fight.team_fight.tournament.id, request)


class TournamentParticipationViewSet(viewsets.ModelViewSet):
    queryset = TournamentParticipation.objects.all()
    serializer_class = TournamentParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentAdminOrReadOnlyDependent)


class TournamentAdminViewSet(viewsets.ModelViewSet):
    queryset = TournamentAdmin.objects.all()
    serializer_class = TournamentAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentOwner)


class ClubAdminViewSet(viewsets.ModelViewSet):
    queryset = ClubAdmin.objects.all()
    serializer_class = ClubAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsClubOwner)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyDependent)

    # TODO: check when will DRF finally release the multiple actions for single url improvement
    @action(
        methods=['post', 'delete'],
        detail=True,
        url_name='members',
        url_path='members/(?P<player_id>[0-9]+)')
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
            player = Player.objects.get(pk=player_id)
            team = Team.objects.get(pk=pk)
            team.team_members.create(player=player)
            return Response(status=status.HTTP_201_CREATED)
        except Player.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @action(
    #     methods=['delete'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<player_id>[0-9]+)')
    def delete_member(self, request, pk=None, player_id=None):
        try:
            player = Player.objects.get(pk=player_id)
            team = Team.objects.get(pk=pk)
            membership = TeamMember.objects.filter(player=player, team=team)
            membership.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Player.DoesNotExist, Team.DoesNotExist, TeamMember.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True)
    def members(self, request, pk=None):
        serializer = PlayerSerializer(Player.objects.filter(team_member__team=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsTournamentAdminDependent])
    def not_assigned(self, request, pk=None):
        serializer = PlayerSerializer(
            Player.objects.filter(participations__tournament__teams=pk)
                .exclude(team_member__team__tournament__teams=pk), many=True)
        return Response(serializer.data)


class PointViewSet(viewsets.ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsPointOwnerOrReadOnly)


class FightViewSet(viewsets.ModelViewSet):
    queryset = Fight.objects.all()
    serializer_class = FightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsFightOwnerOrReadOnly)

    @action(
        methods=['get'],
        detail=True,
        url_name='points')
    def points(self, request, pk=None):
        fight = get_object_or_404(self.queryset, pk=pk)
        serializer = PointSerializer(Point.objects.filter(fight=fight), many=True)
        return Response(serializer.data)


class TeamFightViewSet(viewsets.ModelViewSet):
    queryset = TeamFight.objects.all()
    serializer_class = TeamFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='fights')
    def fights(self, request, pk=None):
        team_fight = get_object_or_404(self.queryset, pk=pk)
        serializer = FightSerializer(Fight.objects.filter(team_fight=team_fight), many=True)
        return Response(serializer.data)


class GroupFightViewSet(viewsets.ModelViewSet):
    queryset = GroupFight.objects.all()
    serializer_class = GroupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsGroupFightOwnerOrReadOnly)


@api_view(['GET'])
def team_fight_authorization(request, pk, format=None):
    team_fight = TeamFight.objects.get(pk=pk)
    return has_tournament_authorization([True, False], team_fight.tournament.id, request)


@api_view(['GET'])
def team_authorization(request, pk, format=None):
    team = get_object_or_404(Team.objects.all(), pk=pk)
    return has_tournament_authorization([True, False], team.tournament.id, request)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsGroupOwnerOrReadOnly)

    # TODO: check when will DRF finally release the multiple actions for single url improvement
    @action(
        methods=['post', 'delete'],
        detail=True,
        url_name='members',
        url_path='members/(?P<team_id>[0-9]+)')
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
            team = Team.objects.get(pk=team_id)
            group = Group.objects.get(pk=pk)
            group.group_memberships.create(team=team)
            return Response(status=status.HTTP_201_CREATED)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Team.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    # @action(
    #     methods=['delete'],
    #     detail=True,
    #     url_name='members',
    #     url_path='members/(?P<team_id>[0-9]+)')
    def delete_member(self, request, pk=None, team_id=None):
        try:
            group = Group.objects.get(pk=pk)
            team = Team.objects.get(pk=team_id)
            membership = GroupMember.objects.filter(group=group, team=team)
            if membership:
                membership.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except (Group.DoesNotExist, Team.DoesNotExist, GroupMember.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True)
    def members(self, request, pk=None):
        serializer = TeamSerializer(Team.objects.filter(group_member__group=pk), many=True)
        return Response(serializer.data)


class GroupPhaseViewSet(viewsets.ModelViewSet):
    queryset = GroupPhase.objects.all()
    serializer_class = GroupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyDependent)

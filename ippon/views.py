from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status, generics
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
            group.group_members.create(team=team)
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

    @action(methods=['get'], detail=True, permission_classes=[
        permissions.IsAuthenticated,
        IsGroupOwnerOrReadOnly])
    def not_assigned(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = TeamSerializer(
            Team.objects.filter(tournament__group_phases__groups=pk)
                .exclude(group_member__group__group_phase__groups=pk), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=True,
        url_name='group_fights')
    def group_fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = GroupFightSerializer(GroupFight.objects.filter(group=pk), many=True)
        return Response(serializer.data)


class GroupPhaseViewSet(viewsets.ModelViewSet):
    queryset = GroupPhase.objects.all()
    serializer_class = GroupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='groups')
    def groups(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = GroupSerializer(Group.objects.filter(group_phase=pk), many=True)
        return Response(serializer.data)


@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save(password=make_password(serializer.validated_data["password"]))
    user.email_user(
        subject="You have been registered",
        message="You have been successfully registered in ippon with username {}".format(
            user.username))

    return Response(status=status.HTTP_201_CREATED, data=serializer.data)


class ShallowPlayerListView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = ShallowPlayerSerializer


class ShallowPlayerDetailView(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = ShallowPlayerSerializer


class CupPhaseViewSet(viewsets.ModelViewSet):
    queryset = CupPhase.objects.all()
    serializer_class = CupPhaseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsTournamentAdminOrReadOnlyDependent)

    @action(
        methods=['get'],
        detail=True,
        url_name='fights')
    def fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = CupFightSerializer(CupFight.objects.filter(cup_phase=pk), many=True)
        return Response(serializer.data)

from django.contrib.auth.hashers import make_password
from django.http.request import HttpRequest
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ErrorDetail
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

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, IsClubOwner))
    def admins(self, request, pk=None):
        serializer = ClubAdminSerializer(ClubAdmin.objects.filter(club=pk), many=True)
        return Response(serializer.data)

    @action(methods=['get'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated, IsClubOwner))
    def non_admins(self, request, pk=None):
        serializer = MinimalUserSerializer(User.objects.exclude(clubs__club=pk), many=True)
        return Response(serializer.data)


class TournamentParticipationViewSet(viewsets.ModelViewSet):
    queryset = TournamentParticipation.objects.all()
    serializer_class = TournamentParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentAdminParticipantCreation)


class TournamentAdminViewSet(viewsets.ModelViewSet):
    queryset = TournamentAdmin.objects.all()
    serializer_class = TournamentAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsTournamentOwnerAdminCreation)


class ClubAdminViewSet(viewsets.ModelViewSet):
    queryset = ClubAdmin.objects.all()
    serializer_class = ClubAdminSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsClubOwnerAdminCreation)


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
        url_path='members/(?P<player_id>[0-9]+)',
        permission_classes=(permissions.IsAuthenticated,
                            IsTeamOwner))
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
        url_path='members/(?P<team_id>[0-9]+)',
        permission_classes=[IsGroupOwner])
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

    @action(methods=['get'],
            detail=True,
            permission_classes=[
                permissions.IsAuthenticated,
                IsGroupOwner])
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

    @action(
        methods=['get'],
        detail=True,
        url_name='member_score',
        url_path='members/(?P<team_id>[0-9]+)/score'
    )
    def member_score(self, request, pk=None, team_id=None):
        group = get_object_or_404(self.queryset, pk=pk)
        team = get_object_or_404(Team.objects.all(), pk=team_id)
        fights = (TeamFight.objects.filter(group_fight__group=pk, aka_team=team_id) \
                  | TeamFight.objects.filter(group_fight__group=pk, shiro_team=team_id)).filter(status=2)
        wins = (fights.filter(aka_team=team_id, winner=1) \
                | fights.filter(shiro_team=team_id, winner=2)).count()

        draws = fights.filter(winner=0, status=2).count()
        points = Point.objects.exclude(type=4) \
            .filter(fight__team_fight__group_fight__group=pk, fight__team_fight__status=2) \
            .filter(Q(fight__team_fight__aka_team=team_id) | Q(fight__team_fight__shiro_team=team_id)) \
            .filter(player__in=team.get_member_ids()).count()

        return Response({"wins": wins, "draws": draws, "points": points, "id": team.id})


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
    """
    Validate input data
    if validation passes it registers the user and returns the sent data
    if validations fails if returns a list of errors in the data
    """

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=False):
        user = serializer.save(password=make_password(serializer.validated_data["password"]))
        user.email_user(
            subject="You have been registered",
            message=f"You have been successfully registered in ippon with username {user.username}")
        return Response(status=status.HTTP_201_CREATED, data=serializer.data, content_type="application/json")
    else:
        response = [str(err[0]) for err in serializer.errors.values()]
        return Response(status=status.HTTP_400_BAD_REQUEST, data=response, content_type="application/json")


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
        url_name='cup_fights')
    def cup_fights(self, request, pk=None):
        get_object_or_404(self.queryset, pk=pk)
        serializer = CupFightSerializer(CupFight.objects.filter(cup_phase=pk), many=True)
        return Response(serializer.data)


class CupFightViewSet(viewsets.ModelViewSet):
    queryset = CupFight.objects.all()
    serializer_class = CupFightSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsCupFightOwnerOrReadOnly)


@api_view(["get"])
def user_data(request: HttpRequest):
    """
    Endpoint for returning basic data about the user currently:
    id, first_name, last_name, username and email
    """
    user: User = request.user
    if user.is_authenticated:
        return Response({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email
        })
    return Response(data={"error": "You are not logged in."}, status=status.HTTP_401_UNAUTHORIZED)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsEventOwnerOrReadOnly]

    # def create(self, request: Request, *args, **kwargs) -> Response:
    #     event = Event()


from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

import ippon.authorization_views
import ippon.club.views
import ippon.player.views
import ippon.point.views
import ippon.team.views
import ippon.team_fight.views
import ippon.tournament.views
from ippon import views

schema_view = get_schema_view(title='ippon_api')

router = DefaultRouter()
router.register(r'players', ippon.player.views.PlayerViewSet)
router.register(r'clubs', ippon.club.views.ClubViewSet)
router.register(r'tournaments', ippon.tournament.views.TournamentViewSet)
router.register(r'participations', ippon.tournament.views.TournamentParticipationViewSet)
router.register(r'tournament_admins', ippon.tournament.views.TournamentAdminViewSet)
router.register(r'club_admins', ippon.club.views.ClubAdminViewSet)
router.register(r'teams', ippon.team.views.TeamViewSet)
router.register(r'points', ippon.point.views.PointViewSet)
router.register(r'fights', views.FightViewSet)
router.register(r'team_fights', ippon.team_fight.views.TeamFightViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'group_phases', views.GroupPhaseViewSet)
router.register(r'group_fights', views.GroupFightViewSet)
router.register(r'cup_phases', views.CupPhaseViewSet)
router.register(r'cup_fights', views.CupFightViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'user-data/', views.user_data, name="user-data"),
    url(r'^schema/', schema_view),
    url(r'^authorization/clubs/(?P<pk>[0-9]+)/$', ippon.authorization_views.club_authorization,
        name='club-authorization'),
    url(r'^authorization/tournaments/staff/(?P<pk>[0-9]+)/$', ippon.authorization_views.tournament_staff_authorization,
        name='tournament-staff-authorization'),
    url(r'^authorization/tournaments/admins/(?P<pk>[0-9]+)/$', ippon.authorization_views.tournament_admin_authorization,
        name='tournament-admin-authorization'),
    url(r'^authorization/fights/(?P<pk>[0-9]+)/$', ippon.authorization_views.fight_authorization,
        name='fight-authorization'),
    url(r'^authorization/team_fights/(?P<pk>[0-9]+)/$', ippon.authorization_views.team_fight_authorization,
        name='team-fight-authorization'),
    url(r'^authorization/teams/(?P<pk>[0-9]+)/$', ippon.authorization_views.team_authorization,
        name='team-authorization'),
    url(r'^authorization/groups/(?P<pk>[0-9]+)/$', ippon.authorization_views.group_authorization,
        name='group-authorization'),
    url(r'^authorization/group_phases/(?P<pk>[0-9]+)/$', ippon.authorization_views.group_phase_authorization,
        name='group-phase-authorization'),
    url(r'^authorization/cup_phases/(?P<pk>[0-9]+)/$', ippon.authorization_views.cup_phase_authorization,
        name='cup-phase-authorization'),
    url(r'^authorization/players/(?P<pk>[0-9]+)/$', ippon.authorization_views.player_authorization,
        name='player-authorization'),
    url(r'^registration/', views.register_user, name='register-user'),
    url(r'^shallow_players/(?P<pk>[0-9]+)/$', ippon.player.views.ShallowPlayerDetailView.as_view(),
        name="shallow-player-detail"),
    url(r'^shallow_players/', ippon.player.views.ShallowPlayerListView.as_view(), name="shallow-player-list")
]

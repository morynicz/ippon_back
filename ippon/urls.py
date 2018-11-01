from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from ippon import views

schema_view = get_schema_view(title='ippon_api')

router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'clubs', views.ClubViewSet)
router.register(r'tournaments', views.TournamentViewSet)
router.register(r'participations', views.TournamentParticipationViewSet)
router.register(r'tournament_admins', views.TournamentAdminViewSet)
router.register(r'club_admins', views.ClubAdminViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'points', views.PointViewSet)
router.register(r'fights', views.FightViewSet)
router.register(r'team_fights', views.TeamFightViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^schema/', schema_view),
    url(r'^authorization/clubs/(?P<pk>[0-9]+)/$', views.club_authorization, name='club-authorization'),
    url(r'^authorization/tournaments/staff/(?P<pk>[0-9]+)/$', views.tournament_staff_authorization,
        name='tournament-staff-authorization'),
    url(r'^authorization/tournaments/admins/(?P<pk>[0-9]+)/$', views.tournament_admin_authorization,
        name='tournament-admin-authorization'),
    url(r'^authorization/fights/(?P<pk>[0-9]+)/$', views.fight_authorization,
        name='fight-authorization'),
    url(r'^authorization/team_fights/(?P<pk>[0-9]+)/$', views.team_fight_authorization,
        name='team-fight-authorization'),
    url(r'^authorization/teams/(?P<pk>[0-9]+)/$', views.team_authorization,
        name='team-authorization'),
]

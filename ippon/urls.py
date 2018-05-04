from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from ippon import views

schema_view = get_schema_view(title='ippon_api')

router = DefaultRouter()
router.register(r'players', views.PlayerViewSet)
router.register(r'clubs', views.ClubViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^schema/', schema_view),
    url(r'^authorization/clubs/(?P<pk>[0-9]+)$', views.club_authorization)
]

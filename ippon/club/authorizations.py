from rest_framework.response import Response

import ippon.models.club as cl


def has_club_authorization(club_id, request):
    try:
        admin = cl.ClubAdmin.objects.get(user=request.user.id, club=club_id)
        is_admin = False
        if admin is not None:
            is_admin = True
        return Response({"isAuthorized": is_admin})

    except cl.ClubAdmin.DoesNotExist:
        return Response({"isAuthorized": False})

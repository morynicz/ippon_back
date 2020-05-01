from rest_framework.response import Response

import ippon.models.tournament as tm


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
import ippon.models.tournament as tm


def is_user_admin_of_the_tournament(request, tournament):
    return tm.TournamentAdmin.objects.filter(tournament=tournament,
                                             user=request.user).count() > 0


def get_tournament_from_dependent(obj):
    return obj.tournament


def has_object_creation_permission(request, serializer_class, tournament_dependent_class_field,
                                   tournament_dependent_class, getter_fcn=get_tournament_from_dependent):
    try:
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tournament_dependent = tournament_dependent_class.objects.get(
            pk=serializer.validated_data[tournament_dependent_class_field].id)
        return is_user_admin_of_the_tournament(request, getter_fcn(tournament_dependent))
    except(KeyError):
        return False
    except tournament_dependent_class.DoesNotExist:
        return False


def get_tournament_from_fight(fight):
    return fight.team_fight.tournament

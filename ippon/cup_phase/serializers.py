from rest_framework import serializers

import ippon.models


class CupPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ippon.models.cup_phase.CupPhase
        fields = (
            "id",
            "tournament",
            "name",
            "fight_length",
            "final_fight_length",
            "number_of_positions",
        )

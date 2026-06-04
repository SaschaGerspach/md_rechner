from rest_framework import serializers

from .data import STATIC


class BuildingSerializer(serializers.Serializer):
    type = serializers.CharField()
    level = serializers.IntegerField()
    workers = serializers.IntegerField(min_value=0)
    allocation = serializers.DictField(child=serializers.FloatField(min_value=0))

    def validate(self, attrs):
        building = STATIC["buildings"].get(attrs["type"])
        if building is None:
            raise serializers.ValidationError(f"unknown building type: {attrs['type']}")
        level = building["levels"].get(attrs["level"])
        if level is None:
            raise serializers.ValidationError(
                f"{attrs['type']} has no level {attrs['level']}"
            )
        known = {r["output"] for r in level["can_produce"]}
        unknown = set(attrs["allocation"]) - known
        if unknown:
            raise serializers.ValidationError(
                f"{attrs['type']} L{attrs['level']} cannot produce: {sorted(unknown)}"
            )
        return attrs


class SettlementSerializer(serializers.Serializer):
    population = serializers.IntegerField(min_value=0)
    buildings = BuildingSerializer(many=True)

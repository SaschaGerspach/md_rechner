from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import calc, graph
from .data import SOURCE, STATIC, VERIFIED
from .serializers import SettlementSerializer


@api_view(["POST"])
def balance(request):
    serializer = SettlementSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    settlement = serializer.validated_data

    errors = calc.validate(settlement, STATIC)
    production, demand, bal = calc.compute_balance(settlement, STATIC)
    return Response(
        {
            "errors": errors,
            "production": production,
            "demand": demand,
            "balance": bal,
            # recipes whose rate is not yet measured contribute nothing; list
            # them so the UI can flag the gap instead of showing a silent zero
            "rates_missing": calc.missing_rates(settlement, STATIC),
        }
    )


@api_view(["GET"])
def buildings(request):
    # serve the static building catalog so the frontend can build its forms;
    # levels are int-keyed internally, exposed as a sorted list with explicit level
    catalog = [
        {
            "id": building_id,
            "levels": [
                {
                    "level": level_no,
                    "max_workers": level["max_workers"],
                    "can_produce": level["can_produce"],
                }
                for level_no, level in sorted(building["levels"].items())
            ],
        }
        for building_id, building in STATIC["buildings"].items()
    ]
    # surface provenance so the UI can mark the data as unverified placeholder
    return Response({"buildings": catalog, "source": SOURCE, "verified": VERIFIED})


@api_view(["GET"])
def chain(request):
    g = graph.build_recipe_graph(STATIC)
    cycles = graph.find_cycles(g)
    return Response(
        {
            "nodes": sorted(g.nodes),
            "edges": [{"source": s, "target": t} for s, t in g.edges],
            "cycles": cycles,
            # topo order is undefined on a cyclic graph; only emit when clean
            "topo_order": [] if cycles else graph.topo_order(g),
        }
    )

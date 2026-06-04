from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import calc, graph
from .data import STATIC
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
        }
    )


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

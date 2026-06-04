"""Production-chain graph over the static recipe data.

A chain like flachs -> leinengarn -> leinengewebe is a directed graph; with
multi-input recipes it is in general a DAG. networkx earns its place here for
topological order (chain layout) and cycle detection (a recipe must never depend
on itself, so a cycle means bad curation). Pure module, no Django dependency.
"""

import networkx as nx


def build_recipe_graph(static):
    g = nx.DiGraph()
    for building in static["buildings"].values():
        for level in building["levels"].values():
            for recipe in level["can_produce"]:
                # a raw producer (no inputs) still needs its output as a node
                g.add_node(recipe["output"])
                for inp in recipe["inputs"]:
                    g.add_edge(inp, recipe["output"])
    return g


def find_cycles(graph):
    return [list(c) for c in nx.simple_cycles(graph)]


def topo_order(graph):
    return list(nx.topological_sort(graph))

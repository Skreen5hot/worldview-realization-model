"""The filter operator F_w(S) = (E, R_w), R_w = {(e, pi, e') in R | pi in Pi_w}. Entities retained; edges filtered."""
from __future__ import annotations
from typing import FrozenSet
from .models import Graph, Family


def filter_graph(graph: Graph, admitted: FrozenSet[str]) -> Graph:
    edges = {eid: e for eid, e in graph.edges.items() if e.predicate in admitted}
    return Graph(dict(graph.entities), edges)


def filter_by_family(graph: Graph, family: Family) -> Graph:
    return filter_graph(graph, family.predicates)


def is_idempotent(graph: Graph, family: Family) -> bool:
    once = filter_by_family(graph, family)
    twice = filter_by_family(once, family)
    return once == twice


def in_scope_entities(graph: Graph) -> FrozenSet[str]:
    """v0.2 §2.3: the in-scope subgraph at w is the union of components of F_w(S) containing at least one edge; its entity set
    is therefore every entity incident to a retained edge."""
    return frozenset(x for e in graph.edges.values() for x in (e.source, e.target))

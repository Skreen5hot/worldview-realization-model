"""Minimal deterministic graph-pattern matcher.

Pattern = {"nodes": {"?v": {"type": ..., "attributes": {...}}}, "edges": [[s, p, t], ...], "constraints": [...]}.
Node variables bind injectively. Bindings are returned in canonical (sorted) order. Every match records the exact
edge IDs that support it. No similarity, no keywords: exact type labels, exact attribute values, exact predicates.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from .models import Graph, Entity

Binding = Dict[str, str]


def node_ok(ent: Entity, spec: Dict[str, Any]) -> bool:
    if spec.get("type") and ent.type != spec["type"]:
        return False
    for k, v in spec.get("attributes", {}).items():
        if ent.attributes.get(k) != v:
            return False
    return True


def _resolve(term: Any, binding: Binding, graph: Graph) -> Any:
    if isinstance(term, str) and term.startswith("?") and "." in term:
        var, attr = term.split(".", 1)
        eid = binding[var]
        return graph.entities[eid].attributes.get(attr)
    return term


def constraints_ok(constraints: List[List[Any]], binding: Binding, graph: Graph) -> bool:
    for c in constraints or []:
        op = c[1]
        a = _resolve(c[0], binding, graph)
        b = _resolve(c[2], binding, graph)
        if a is None or b is None:
            return False
        if op == "<":
            if not (a < b):
                return False
        elif op == "<=":
            if not (a <= b):
                return False
        elif op == "==":
            if not (a == b):
                return False
        elif op == "within":
            hi = _resolve(c[3], binding, graph)
            if hi is None or not (b <= a <= hi):
                return False
        else:
            raise ValueError(f"unknown constraint op {op}")
    return True


def match(pattern: Dict[str, Any], graph: Graph, initial: Optional[Binding] = None) -> List[Tuple[Binding, List[str]]]:
    """Return every (binding, supporting_edge_ids) for which all pattern edges exist in `graph` and node specs and
    constraints hold. `initial` pre-binds variables (used for prescribed-pattern extensions)."""
    nodes: Dict[str, Dict[str, Any]] = pattern.get("nodes", {})
    edges: List[List[str]] = pattern.get("edges", [])
    constraints = pattern.get("constraints", [])
    results: List[Tuple[Binding, List[str]]] = []
    seen = set()

    def bind_var(binding: Binding, var: str, eid: str) -> Optional[Binding]:
        if var in binding:
            return binding if binding[var] == eid else None
        spec = nodes.get(var, {})
        ent = graph.entities.get(eid)
        if ent is None or not node_ok(ent, spec):
            return None
        if eid in binding.values():  # injective
            return None
        nb = dict(binding)
        nb[var] = eid
        return nb

    def rec(i: int, binding: Binding, support: List[str]):
        if i == len(edges):
            # bind any remaining edge-free variables (rare: pattern with isolated nodes)
            free = [v for v in nodes if v not in binding]
            if free:
                v = free[0]
                for eid in sorted(graph.entities):
                    nb = bind_var(binding, v, eid)
                    if nb is not None:
                        rec(i, nb, support)
                return
            if constraints_ok(constraints, binding, graph):
                key = tuple(sorted(binding.items()))
                if key not in seen:
                    seen.add(key)
                    results.append((dict(binding), sorted(support)))
            return
        s, p, t = edges[i]
        for e in graph.edges_with_predicate(p):
            b1 = bind_var(binding, s, e.source)
            if b1 is None:
                continue
            b2 = bind_var(b1, t, e.target)
            if b2 is None:
                continue
            rec(i + 1, b2, support + [e.edge_id])

    rec(0, dict(initial or {}), [])
    results.sort(key=lambda r: (tuple(sorted(r[0].items())), tuple(r[1])))
    return results


def pattern_predicates(pattern: Dict[str, Any]) -> frozenset:
    return frozenset(p for _, p, _ in pattern.get("edges", []))

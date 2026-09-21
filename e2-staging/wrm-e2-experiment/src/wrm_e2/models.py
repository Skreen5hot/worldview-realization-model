"""Core data structures: the situation graph S = (E, R), families, and loaders.

Everything is plain dataclasses over JSON so that artifacts stay inspectable.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"

FROZEN_ARTIFACTS = {
    "scenario": DATA_DIR / "scenario.json",
    "ontology_predicates": DATA_DIR / "ontology_predicates.json",
    "assignments": DATA_DIR / "assignments.json",
    "reference_library": DATA_DIR / "reference_library.json",
    "objectives": DATA_DIR / "objectives.json",
    "perturbations": DATA_DIR / "perturbations.json",
    "firewall_lexicon": DATA_DIR / "firewall_lexicon.json",
    "metric": CONFIG_DIR / "metric.json",
    "experiment": CONFIG_DIR / "experiment.json",
    "experiment_protocol": ROOT / "docs" / "experiment_protocol.md",
}


@dataclass(frozen=True)
class Entity:
    id: str
    type: str
    label: str
    type_iri: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    edge_id: str
    source: str
    predicate: str
    target: str

    def triple(self) -> Tuple[str, str, str]:
        return (self.source, self.predicate, self.target)


@dataclass
class Graph:
    """S = (E, R). Entities keyed by id; edges keyed by edge_id. Order-independent equality."""
    entities: Dict[str, Entity]
    edges: Dict[str, Edge]

    @property
    def predicates(self) -> FrozenSet[str]:
        return frozenset(e.predicate for e in self.edges.values())

    def edge_ids(self) -> List[str]:
        return sorted(self.edges)

    def edges_with_predicate(self, predicate: str) -> List[Edge]:
        return sorted((e for e in self.edges.values() if e.predicate == predicate), key=lambda e: e.edge_id)

    def out_edges(self, source: str, predicate: Optional[str] = None) -> List[Edge]:
        return sorted((e for e in self.edges.values() if e.source == source and (predicate is None or e.predicate == predicate)), key=lambda e: e.edge_id)

    def has_triple(self, s: str, p: str, t: str) -> Optional[Edge]:
        for e in self.edges.values():
            if e.source == s and e.predicate == p and e.target == t:
                return e
        return None

    def copy(self) -> "Graph":
        return Graph(dict(self.entities), dict(self.edges))

    def to_json(self) -> Dict[str, Any]:
        return {
            "entities": [entity_to_json(e) for e in sorted(self.entities.values(), key=lambda x: x.id)],
            "edges": [edge_to_json(e) for e in sorted(self.edges.values(), key=lambda x: x.edge_id)],
        }

    def __eq__(self, other):
        return isinstance(other, Graph) and self.entities == other.entities and self.edges == other.edges


def entity_to_json(e: Entity) -> Dict[str, Any]:
    return {"id": e.id, "type": e.type, "type_iri": e.type_iri, "label": e.label, "attributes": dict(e.attributes)}


def edge_to_json(e: Edge) -> Dict[str, Any]:
    return {"edge_id": e.edge_id, "source": e.source, "predicate": e.predicate, "target": e.target}


def graph_from_json(doc: Dict[str, Any]) -> Graph:
    ents = {}
    for e in doc["entities"]:
        ents[e["id"]] = Entity(id=e["id"], type=e["type"], label=e.get("label", e["id"]), type_iri=e.get("type_iri", ""),
                               attributes=dict(e.get("attributes", {})))
    edges = {}
    for r in doc["edges"]:
        edges[r["edge_id"]] = Edge(edge_id=r["edge_id"], source=r["source"], predicate=r["predicate"], target=r["target"])
    return Graph(ents, edges)


@dataclass(frozen=True)
class Family:
    name: str
    predicates: FrozenSet[str]
    boundary: FrozenSet[str]
    criterion: str = ""


@dataclass
class Assignment:
    families: List[Family]

    def by_name(self, name: str) -> Family:
        for f in self.families:
            if f.name == name:
                return f
        raise KeyError(name)

    def names(self) -> List[str]:
        return [f.name for f in self.families]

    def to_json(self) -> Dict[str, Any]:
        return {"families": [{"family": f.name, "predicates": sorted(f.predicates), "boundary": sorted(f.boundary)} for f in self.families]}


def assignment_from_json(doc: Dict[str, Any]) -> Assignment:
    fams = []
    for f in doc["families"]:
        preds = frozenset(p["predicate_id"] for p in f["predicates"])
        boundary = frozenset(p["predicate_id"] for p in f["predicates"] if p.get("boundary"))
        fams.append(Family(name=f["family"], predicates=preds, boundary=boundary, criterion=f.get("criterion", "")))
    return Assignment(fams)


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@dataclass
class Bundle:
    """All frozen inputs, loaded once."""
    scenario_doc: Dict[str, Any]
    graph: Graph
    predicates_doc: Dict[str, Any]
    assignment_doc: Dict[str, Any]
    assignment: Assignment
    library_doc: Dict[str, Any]
    objectives_doc: Dict[str, Any]
    perturbations_doc: Dict[str, Any]
    lexicon_doc: Dict[str, Any]
    metric: Dict[str, Any]
    experiment: Dict[str, Any]

    @property
    def vocabulary(self) -> FrozenSet[str]:
        return frozenset(p["id"] for p in self.predicates_doc["predicates"])

    @property
    def reference_conditions(self) -> List[Dict[str, Any]]:
        return self.library_doc["reference_conditions"]

    @property
    def objectives(self) -> Dict[str, Dict[str, Any]]:
        return {o["id"]: o for o in self.objectives_doc["objectives"]}


def load_bundle(root: Path = ROOT) -> Bundle:
    d = root / "data"
    c = root / "config"
    scenario_doc = load_json(d / "scenario.json")
    assignment_doc = load_json(d / "assignments.json")
    return Bundle(
        scenario_doc=scenario_doc,
        graph=graph_from_json(scenario_doc),
        predicates_doc=load_json(d / "ontology_predicates.json"),
        assignment_doc=assignment_doc,
        assignment=assignment_from_json(assignment_doc),
        library_doc=load_json(d / "reference_library.json"),
        objectives_doc=load_json(d / "objectives.json"),
        perturbations_doc=load_json(d / "perturbations.json"),
        lexicon_doc=load_json(d / "firewall_lexicon.json"),
        metric=load_json(c / "metric.json"),
        experiment=load_json(c / "experiment.json"),
    )

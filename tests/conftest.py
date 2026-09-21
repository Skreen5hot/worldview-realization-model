import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from wrm_poc.models import load_bundle, Graph, Entity, Edge, Family, Assignment


@pytest.fixture(scope="session")
def bundle():
    return load_bundle()


def tiny_graph():
    """Constructed graph: a spec prescribes a quality borne by an artifact, one measurement in spec, one out."""
    ents = {
        "S": Entity("S", "Dimension Specification", "spec", attributes={"lower": 1.0, "upper": 2.0}),
        "A1": Entity("A1", "Portion of Processed Material", "lot1"), "A2": Entity("A2", "Portion of Processed Material", "lot2"),
        "Q1": Entity("Q1", "quality", "q1"), "Q2": Entity("Q2", "quality", "q2"),
        "M1": Entity("M1", "Ratio Measurement Information Content Entity", "m1", attributes={"value": 1.5}),
        "M2": Entity("M2", "Ratio Measurement Information Content Entity", "m2", attributes={"value": 2.5}),
        "P": Entity("P", "Person", "p"), "R": Entity("R", "Occupation Role", "r"),
    }
    edges = [("S", "prescribes", "Q1"), ("S", "prescribes", "Q2"), ("A1", "bearer_of", "Q1"), ("A2", "bearer_of", "Q2"),
             ("M1", "is_a_measurement_of", "Q1"), ("M2", "is_a_measurement_of", "Q2"), ("P", "bearer_of", "R")]
    return Graph(ents, {f"T{i:02d}": Edge(f"T{i:02d}", s, p, t) for i, (s, p, t) in enumerate(edges)})


RC_TINY = {
    "id": "RC-T", "label": "tiny conformance", "domain": "x", "description": "x",
    "applicability": {"nodes": {"?spec": {"type": "Dimension Specification"}, "?q": {"type": "quality"}, "?m": {}, "?lot": {"type": "Portion of Processed Material"}},
                      "edges": [["?spec", "prescribes", "?q"], ["?m", "is_a_measurement_of", "?q"], ["?lot", "bearer_of", "?q"]]},
    "prescribed": {"kind": "value_constraint", "constraints": [["?m.value", "within", "?spec.lower", "?spec.upper"]]},
    "objectives": [{"objective": "OBJ-01", "rationale": "r"}], "remediation": {}, "satisfaction_condition": "in spec",
}

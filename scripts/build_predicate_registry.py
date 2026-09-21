"""Authoring aid: build data/ontology_predicates.json from a parsed CCO merged ontology.

Run once during development against a local clone of CommonCoreOntology/CommonCoreOntologies.
The produced JSON is the frozen artifact; this script is provenance for how it was produced.
Usage: python scripts/build_predicate_registry.py <objprops.json from scratchpad index> data/ontology_predicates.json
"""
import json, sys

# id -> (label in CCO, primary MRC domain, relational_domain note, verification note)
ADMITTED = {
    "bearer_of": ("bearer of", "physical_causal", "independent continuant -> specifically dependent continuant (quality, role, disposition)"),
    "has_continuant_part": ("has continuant part", "physical_causal", "continuant -> continuant (mereology)"),
    "has_participant": ("has participant", "physical_causal", "process -> continuant"),
    "has_output": ("has output", "physical_causal", "process -> continuant produced by the process"),
    "has_input": ("has input", "informational", "process -> continuant consumed/used as input (in this vocabulary: information content)"),
    "is_cause_of": ("is cause of", "physical_causal", "process -> process (consequence)"),
    "precedes": ("precedes", "physical_causal", "occurrent -> occurrent (temporal order)"),
    "realizes": ("realizes", "agentic", "process -> realizable entity (role/disposition/function)"),
    "has_agent": ("has agent", "agentic", "process -> Agent playing a causative role"),
    "uses": ("uses", "agentic", "Agent -> material entity leveraged in a process"),
    "has_recipient": ("has recipient", "informational", "Act of Communication -> Agent receiving it"),
    "is_about": ("is about", "informational", "Information Content Entity -> entity"),
    "is_a_measurement_of": ("is a measurement of", "informational", "Measurement ICE -> entity measured"),
    "prescribes": ("prescribes", "legal_institutional", "Prescriptive ICE -> entity it rules/guides/models"),
    "has_organizational_context": ("has organizational context", "legal_institutional", "role -> Organization"),
    "is_subordinate_role_to": ("is subordinate role to", "legal_institutional", "role -> role (regulatory authority chain)"),
    "is_affiliated_with": ("is affiliated with", "legal_institutional", "Agent -> Agent (social/business relationship)"),
    "affects": ("affects", "evaluative_experiential", "process -> entity influenced by it (here: persons/organizations touched by a process)"),
    "has_interest_in": ("has interest in", "evaluative_experiential", "Agent -> process in which the agent has an interest"),
    "supervises": ("supervises", "agentic", "Person -> Person"),
}

def main(src, dst):
    props = json.load(open(src))
    bylabel = {v["label"]: v for v in props.values()}
    out = []
    for pid, (label, mrc, note) in ADMITTED.items():
        v = bylabel[label]
        def lab(lst, labs):
            res = []
            for iri, l in zip(lst, labs):
                if l is None or iri.startswith("n"):
                    res.append("(anonymous union class)" if (l is None) else l)
                else:
                    res.append(l)
            return ", ".join(res) if res else "(unrestricted)"
        iri = v["iri"]
        source = "BFO 2020 (as imported by CCO 2.0 merged)" if "obo/BFO" in iri else "CCO 2.0 Extended Relation Ontology / Agent Ontology (merged file)"
        out.append({
            "id": pid,
            "iri": iri,
            "label": label,
            "domain": lab(v["domain"], v["domain_label"]),
            "range": lab(v["range"], v["range_label"]),
            "parent_property": ", ".join(p for p in v["parent_label"] if p) or "(none)",
            "relational_domain": mrc,
            "relational_note": note,
            "source": source,
            "definition": v["definition"],
            "verification_status": "verified",
            "verification_method": "label+IRI+definition+domain+range+parent read from CommonCoreOntologiesMerged.ttl via rdflib",
        })
    json.dump({"schema": "wrm-poc/ontology_predicates/v1", "predicates": out}, open(dst, "w"), indent=2)
    print(len(out), "predicates written")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

"""Authoring aid for data/scenario.json (the JSON file is the frozen artifact; this script is provenance)."""
import json, sys

T = {
  "Commercial Organization": "https://www.commoncoreontologies.org/ont00000443",
  "Organization": "https://www.commoncoreontologies.org/ont00001180",
  "Government Organization": "https://www.commoncoreontologies.org/ont00000408",
  "Person": "https://www.commoncoreontologies.org/ont00001262",
  "Group of Persons": "https://www.commoncoreontologies.org/ont00000914",
  "Occupation Role": "https://www.commoncoreontologies.org/ont00000984",
  "Portion of Processed Material": "https://www.commoncoreontologies.org/ont00001084",
  "quality": "http://purl.obolibrary.org/obo/BFO_0000019",
  "disposition": "http://purl.obolibrary.org/obo/BFO_0000016",
  "Ratio Measurement Information Content Entity": "https://www.commoncoreontologies.org/ont00001022",
  "Act of Measuring": "https://www.commoncoreontologies.org/ont00000345",
  "Material Artifact": "https://www.commoncoreontologies.org/ont00000995",
  "Dimension Specification": "https://www.commoncoreontologies.org/ont00001304",
  "Report": "https://www.commoncoreontologies.org/ont00002043",
  "Prescriptive Information Content Entity": "https://www.commoncoreontologies.org/ont00000965",
  "Certificate": "https://www.commoncoreontologies.org/ont00002002",
  "Process Regulation": "https://www.commoncoreontologies.org/ont00001324",
  "Plan": "https://www.commoncoreontologies.org/ont00000974",
  "Act of Manufacturing": "https://www.commoncoreontologies.org/ont00001359",
  "Act of Reporting": "https://www.commoncoreontologies.org/ont00000151",
  "Email Messaging": "https://www.commoncoreontologies.org/ont00000492",
  "Planned Act": "https://www.commoncoreontologies.org/ont00000228",
  "Act of Cargo Transportation": "https://www.commoncoreontologies.org/ont00000595",
  "Act of Communication": "https://www.commoncoreontologies.org/ont00000402",
  "Act of Artifact Employment": "https://www.commoncoreontologies.org/ont00000566",
  "Act": "https://www.commoncoreontologies.org/ont00000005",
  "Act of Artifact Modification": "https://www.commoncoreontologies.org/ont00000970",
}

def ent(id_, type_, label, **attrs):
    return {"id": id_, "type": type_, "type_iri": T[type_], "label": label, "attributes": attrs}

E = [
  ent("ORG-NPC", "Commercial Organization", "Northline Precision Components"),
  ent("ORG-HTA", "Organization", "Harbor Transit Authority"),
  ent("ORG-REG", "Government Organization", "Vehicle Component Safety Office"),
  ent("P-ENG", "Person", "Dana Okafor"),
  ent("P-QM", "Person", "Ruth Salazar"),
  ent("P-PM", "Person", "Victor Lindqvist"),
  ent("P-INSP", "Person", "Miguel Ortega"),
  ent("AGG-PASS", "Group of Persons", "Harbor Transit bus passengers"),
  ent("R-ENG", "Occupation Role", "process engineer role", kind="engineering"),
  ent("R-QM", "Occupation Role", "quality manager role", kind="quality_management"),
  ent("R-PM", "Occupation Role", "plant manager role", kind="management"),
  ent("R-INSP", "Occupation Role", "dimensional inspector role", kind="inspection"),
  ent("A-MILL", "Material Artifact", "machining center MC-7"),
  ent("A-CMM", "Material Artifact", "coordinate measuring machine CMM-2"),
  ent("A-ACT", "Material Artifact", "brake actuator assembly batch 2026-Q3"),
  ent("D-LEAK", "disposition", "internal leakage disposition of valve body lot 4", safety_relevant=True),
  ent("SPEC", "Dimension Specification", "valve body bore diameter specification VB-12", lower=11.990, upper=12.010, unit="mm", quality_kind="bore_diameter"),
  ent("NCR", "Report", "nonconformance report NCR-0417", kind="nonconformance_report", safety_relevant=True),
  ent("DIR-CONT", "Prescriptive Information Content Entity", "directive: continue production and ship lot 4", kind="directive"),
  ent("CERT", "Certificate", "certificate of conformance for valve body lot 4", asserts_conformance=True),
  ent("REG", "Process Regulation", "safety-related nonconformance notification regulation", kind="regulation"),
  ent("SCHED", "Plan", "Q3 delivery schedule", kind="schedule"),
  ent("ACT-MFG", "Act of Manufacturing", "machining of valve body lots 1-4"),
  ent("ACT-NCR", "Act of Reporting", "writing of nonconformance report NCR-0417", kind="nonconformance_reporting"),
  ent("ACT-EMAIL", "Email Messaging", "escalation email of NCR-0417 to management", kind="escalation"),
  ent("ACT-REPLY", "Email Messaging", "acknowledgement reply from quality manager", kind="acknowledgement"),
  ent("ACT-DEC", "Planned Act", "production continuation decision", kind="decision"),
  ent("ACT-SHIP", "Act of Cargo Transportation", "shipment of valve body lot 4 to Harbor Transit"),
  ent("ACT-SHIPNOTE", "Act of Communication", "shipping notice with certificate to Harbor Transit", kind="shipping_notice"),
  ent("PROC-BRAKE", "Act of Artifact Employment", "in-service brake actuation on Harbor Transit buses", kind="operational_use"),
  ent("PROC-QMS", "Act", "Northline quality management process", kind="quality_management_process"),
]
values = [12.003, 12.006, 12.009, 12.013]
for i in range(1, 5):
    E.append(ent(f"LOT-{i}", "Portion of Processed Material", f"valve body lot {i}"))
    E.append(ent(f"Q-{i}", "quality", f"bore diameter of valve body lot {i}", quality_kind="bore_diameter"))
    E.append(ent(f"M-{i}", "Ratio Measurement Information Content Entity", f"bore diameter measurement of lot {i}", value=values[i-1], unit="mm", measurand_kind="bore_diameter"))
    E.append(ent(f"ACT-M{i}", "Act of Measuring", f"dimensional inspection of lot {i}", sequence=i))

R = [
  # roles and organization
  ("P-ENG","bearer_of","R-ENG"), ("P-QM","bearer_of","R-QM"), ("P-PM","bearer_of","R-PM"), ("P-INSP","bearer_of","R-INSP"),
  ("R-ENG","has_organizational_context","ORG-NPC"), ("R-QM","has_organizational_context","ORG-NPC"),
  ("R-PM","has_organizational_context","ORG-NPC"), ("R-INSP","has_organizational_context","ORG-NPC"),
  ("R-ENG","is_subordinate_role_to","R-QM"), ("R-QM","is_subordinate_role_to","R-PM"), ("R-ENG","is_subordinate_role_to","R-PM"),
  ("P-QM","supervises","P-ENG"), ("P-PM","supervises","P-QM"),
  ("ORG-NPC","is_affiliated_with","ORG-HTA"),
  # manufacturing
  ("ACT-MFG","has_agent","ORG-NPC"), ("ACT-MFG","has_participant","A-MILL"), ("ORG-NPC","uses","A-MILL"),
  ("ACT-MFG","has_output","LOT-1"), ("ACT-MFG","has_output","LOT-2"), ("ACT-MFG","has_output","LOT-3"), ("ACT-MFG","has_output","LOT-4"),
  # qualities and specification
  ("LOT-1","bearer_of","Q-1"), ("LOT-2","bearer_of","Q-2"), ("LOT-3","bearer_of","Q-3"), ("LOT-4","bearer_of","Q-4"),
  ("SPEC","prescribes","Q-1"), ("SPEC","prescribes","Q-2"), ("SPEC","prescribes","Q-3"), ("SPEC","prescribes","Q-4"),
  # measurement
  ("ACT-M1","has_participant","LOT-1"), ("ACT-M2","has_participant","LOT-2"), ("ACT-M3","has_participant","LOT-3"), ("ACT-M4","has_participant","LOT-4"),
  ("ACT-M1","has_output","M-1"), ("ACT-M2","has_output","M-2"), ("ACT-M3","has_output","M-3"), ("ACT-M4","has_output","M-4"),
  ("M-1","is_a_measurement_of","Q-1"), ("M-2","is_a_measurement_of","Q-2"), ("M-3","is_a_measurement_of","Q-3"), ("M-4","is_a_measurement_of","Q-4"),
  ("ACT-M1","precedes","ACT-M2"), ("ACT-M2","precedes","ACT-M3"), ("ACT-M3","precedes","ACT-M4"),
  ("ACT-M1","has_agent","P-INSP"), ("ACT-M2","has_agent","P-INSP"), ("ACT-M3","has_agent","P-INSP"), ("ACT-M4","has_agent","P-INSP"),
  ("P-INSP","uses","A-CMM"), ("ACT-M4","has_participant","A-CMM"), ("ACT-M4","realizes","R-INSP"),
  # reporting
  ("ACT-NCR","has_agent","P-ENG"), ("ACT-NCR","realizes","R-ENG"),
  ("ACT-NCR","has_input","M-2"), ("ACT-NCR","has_input","M-3"), ("ACT-NCR","has_input","M-4"),
  ("ACT-NCR","has_output","NCR"), ("NCR","is_about","LOT-4"), ("NCR","is_about","Q-4"),
  ("ACT-M4","precedes","ACT-NCR"), ("ACT-NCR","precedes","ACT-EMAIL"),
  # escalation
  ("ACT-EMAIL","has_agent","P-ENG"), ("ACT-EMAIL","has_input","NCR"), ("ACT-EMAIL","has_recipient","P-QM"), ("ACT-EMAIL","has_recipient","P-PM"),
  ("ACT-REPLY","has_agent","P-QM"), ("ACT-REPLY","has_recipient","P-ENG"), ("ACT-EMAIL","precedes","ACT-REPLY"), ("ACT-EMAIL","precedes","ACT-DEC"),
  # decision
  ("ACT-DEC","has_agent","P-PM"), ("ACT-DEC","realizes","R-PM"), ("ACT-DEC","has_input","SCHED"), ("ACT-DEC","has_output","DIR-CONT"),
  ("DIR-CONT","prescribes","ACT-SHIP"), ("DIR-CONT","is_about","LOT-4"), ("ACT-DEC","is_cause_of","ACT-SHIP"), ("ACT-DEC","precedes","ACT-SHIP"),
  ("SCHED","prescribes","ACT-SHIP"),
  # shipment and customer
  ("ACT-SHIP","has_agent","ORG-NPC"), ("ACT-SHIP","has_participant","LOT-4"), ("ACT-SHIP","affects","ORG-HTA"),
  ("ACT-SHIPNOTE","has_agent","ORG-NPC"), ("ACT-SHIPNOTE","has_recipient","ORG-HTA"), ("ACT-SHIPNOTE","has_input","CERT"), ("CERT","is_about","LOT-4"),
  ("A-ACT","has_continuant_part","LOT-4"), ("ORG-HTA","uses","A-ACT"),
  ("PROC-BRAKE","has_agent","ORG-HTA"), ("PROC-BRAKE","has_participant","A-ACT"), ("PROC-BRAKE","has_participant","LOT-4"),
  ("PROC-BRAKE","affects","AGG-PASS"), ("AGG-PASS","has_interest_in","PROC-BRAKE"), ("ORG-HTA","has_interest_in","PROC-BRAKE"),
  ("ACT-SHIP","precedes","PROC-BRAKE"), ("LOT-4","bearer_of","D-LEAK"),
  # institutional
  ("REG","prescribes","PROC-QMS"), ("PROC-QMS","has_agent","ORG-NPC"), ("PROC-QMS","realizes","R-QM"), ("ORG-REG","has_interest_in","PROC-QMS"),
]
edges = [{"edge_id": f"E{i+1:03d}", "source": s, "predicate": p, "target": t} for i, (s, p, t) in enumerate(R)]
doc = {
  "schema": "wrm-poc/scenario/v1",
  "metadata_excluded_from_experiment": {
    "title": "Valve body bore-diameter drift at a brake-component supplier",
    "note": "Frozen situation graph S=(E,R). Facts only; no appraisal encoded. Authored for the WRM proof-of-concept.",
  },
  "entities": E,
  "edges": edges,
}
json.dump(doc, open(sys.argv[1], "w"), indent=1)
print(len(E), "entities", len(edges), "edges", len({e['predicate'] for e in edges}), "predicate types")

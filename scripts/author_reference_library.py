"""Authoring aid for data/reference_library.json (frozen artifact is the JSON)."""
import json, sys

def node(type_=None, **attrs):
    d = {}
    if type_: d["type"] = type_
    if attrs: d["attributes"] = attrs
    return d

RC = []
def rc(id_, label, domain, description, alpha, prescribed, objectives, remediation, satisfaction):
    RC.append({"id": id_, "label": label, "domain": domain, "description": description,
               "applicability": alpha, "prescribed": prescribed, "objectives": objectives,
               "remediation": remediation, "satisfaction_condition": satisfaction})

# ---- artifact / specification conformance
rc("RC-01", "Specification conformance of a measured quality", "artifact_specification_conformance",
   "Where a specification prescribes a quality borne by an artifact and a measurement of that quality exists, the measured value must lie within the specification's prescribed bounds.",
   {"nodes": {"?spec": node("Dimension Specification"), "?q": node("quality"), "?m": node("Ratio Measurement Information Content Entity"), "?lot": node("Portion of Processed Material")},
    "edges": [["?spec","prescribes","?q"], ["?m","is_a_measurement_of","?q"], ["?lot","bearer_of","?q"]]},
   {"kind": "value_constraint", "constraints": [["?m.value", "within", "?spec.lower", "?spec.upper"]]},
   [{"objective": "OBJ-01", "rationale": "A measured value outside the prescribed bounds is a direct non-conformity of the artifact to its specification."}],
   {"value_fact_steps": [
       {"action_type": "rework_or_segregate", "operation": "create", "relation": "has_participant", "source": "NEW:Act of Artifact Modification:rework", "target": "?lot", "actor": "responder", "effect": "bring the artifact's quality back within the prescribed bounds or segregate it"}]},
   "Every measurement of the prescribed quality lies within the specification bounds, or the artifact is segregated by a rework act.")

rc("RC-02", "Drift response in a measurement sequence", "quality_process_monitoring",
   "Where three successive measuring acts on lots from the same manufacturing act produce monotonically increasing values of the same measurand, an act of artifact modification on the producing machine must follow the third measuring act.",
   {"nodes": {"?a1": node("Act of Measuring"), "?a2": node("Act of Measuring"), "?a3": node("Act of Measuring"),
              "?m1": node(), "?m2": node(), "?m3": node(), "?lot3": node("Portion of Processed Material"), "?mfg": node("Act of Manufacturing"), "?mach": node("Material Artifact")},
    "edges": [["?a1","precedes","?a2"], ["?a2","precedes","?a3"], ["?a1","has_output","?m1"], ["?a2","has_output","?m2"], ["?a3","has_output","?m3"],
              ["?a3","has_participant","?lot3"], ["?mfg","has_output","?lot3"], ["?mfg","has_participant","?mach"]],
    "constraints": [["?m1.value", "<", "?m2.value"], ["?m2.value", "<", "?m3.value"], ["?m1.measurand_kind", "==", "?m3.measurand_kind"]]},
   {"kind": "exists", "nodes": {"?adj": node("Act of Artifact Modification")}, "edges": [["?adj","has_participant","?mach"], ["?a3","precedes","?adj"]]},
   [{"objective": "OBJ-01", "rationale": "An unanswered monotone drift foreseeably carries the produced quality out of conformity."}],
   {}, "An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.")

rc("RC-03", "Corrective action on a nonconformance report", "quality_process_monitoring",
   "Where a nonconformance report is about a lot, a corrective-action act taking that report as input must exist.",
   {"nodes": {"?ncr": node("Report", kind="nonconformance_report"), "?lot": node("Portion of Processed Material")}, "edges": [["?ncr","is_about","?lot"]]},
   {"kind": "exists", "nodes": {"?ca": node("Planned Act", kind="corrective_action")}, "edges": [["?ca","has_input","?ncr"]]},
   [{"objective": "OBJ-03", "rationale": "Quality-system obligations require every nonconformance report to be closed by a corrective action."}],
   {}, "A corrective-action act has the nonconformance report as input.")

rc("RC-04", "Nonconforming product control in directives", "artifact_specification_conformance",
   "Where a nonconformance report and a directive are both about the same lot and the directive is the output of a decision act, that decision act must have the report as input.",
   {"nodes": {"?ncr": node("Report", kind="nonconformance_report"), "?dir": node(kind="directive"), "?lot": node("Portion of Processed Material"), "?dec": node()},
    "edges": [["?ncr","is_about","?lot"], ["?dir","is_about","?lot"], ["?dec","has_output","?dir"]]},
   {"kind": "exists", "nodes": {}, "edges": [["?dec","has_input","?ncr"]]},
   [{"objective": "OBJ-03", "rationale": "Disposition of nonconforming product must be decided with the nonconformance record before it."},
    {"objective": "OBJ-05", "rationale": "A directive about a lot issued without its nonconformance record is a decision made on incomplete information."}],
   {}, "The decision act that produced the directive has the nonconformance report as input.")

rc("RC-05", "Hazard control before operational use", "safety_escalation",
   "Where a safety-relevant disposition is borne by a lot that participates in an operational-use process, a hazard-control act on the lot must precede that use.",
   {"nodes": {"?lot": node("Portion of Processed Material"), "?d": node("disposition", safety_relevant=True), "?use": node(kind="operational_use")},
    "edges": [["?lot","bearer_of","?d"], ["?use","has_participant","?lot"]]},
   {"kind": "exists", "nodes": {"?ctrl": node("Planned Act", kind="hazard_control")}, "edges": [["?ctrl","has_participant","?lot"], ["?ctrl","precedes","?use"]]},
   [{"objective": "OBJ-02", "rationale": "A safety-relevant disposition in service without prior control is a foreseeable path to harm."}],
   {}, "A hazard-control act on the lot precedes its operational use.")

rc("RC-06", "Completeness of conformance communication", "reporting_communication",
   "Where a communication delivers a conformance-asserting certificate about a lot to a recipient and a nonconformance report about the same lot exists, a communication delivering that report to the same recipient must exist.",
   {"nodes": {"?c": node(), "?cert": node("Certificate", asserts_conformance=True), "?party": node(), "?lot": node("Portion of Processed Material"), "?ncr": node("Report", kind="nonconformance_report")},
    "edges": [["?c","has_input","?cert"], ["?c","has_recipient","?party"], ["?cert","is_about","?lot"], ["?ncr","is_about","?lot"]]},
   {"kind": "exists", "nodes": {"?c2": node("Act of Communication")}, "edges": [["?c2","has_input","?ncr"], ["?c2","has_recipient","?party"]]},
   [{"objective": "OBJ-04", "rationale": "A recipient who holds only the conformance assertion cannot exercise informed judgment about the lot."}],
   {}, "The recipient of the certificate has also received the nonconformance report.")

rc("RC-07", "Role obligation to report upward", "role_obligation",
   "Where a person in a role performs a nonconformance-reporting act and their role is subordinate to another role, they must communicate to the bearer of the superior role.",
   {"nodes": {"?a": node(kind="nonconformance_reporting"), "?p": node("Person"), "?r1": node("Occupation Role"), "?r2": node("Occupation Role"), "?sup": node("Person")},
    "edges": [["?a","has_agent","?p"], ["?p","bearer_of","?r1"], ["?r1","is_subordinate_role_to","?r2"], ["?sup","bearer_of","?r2"]]},
   {"kind": "exists", "nodes": {"?c": node()}, "edges": [["?c","has_agent","?p"], ["?c","has_recipient","?sup"]]},
   [{"objective": "OBJ-03", "rationale": "Upward reporting is an obligation attached to a subordinate role."}],
   {}, "The reporting person has communicated to each bearer of a superior role.")

rc("RC-08", "Supervisory response to an escalation", "role_obligation",
   "Where an escalation communication from a subordinate is received by the bearer of a superior role, the superior must perform an act with the subordinate as recipient.",
   {"nodes": {"?c": node(kind="escalation"), "?sup": node("Person"), "?p": node("Person"), "?r1": node("Occupation Role"), "?r2": node("Occupation Role")},
    "edges": [["?c","has_recipient","?sup"], ["?c","has_agent","?p"], ["?p","bearer_of","?r1"], ["?r1","is_subordinate_role_to","?r2"], ["?sup","bearer_of","?r2"]]},
   {"kind": "exists", "nodes": {"?r": node()}, "edges": [["?r","has_agent","?sup"], ["?r","has_recipient","?p"]]},
   [{"objective": "OBJ-05", "rationale": "An escalation with no response leaves the organization's information loop open."}],
   {}, "Each superior who received the escalation has performed an act with the escalating person as recipient.")

rc("RC-09", "Information to interested parties about a hazardous lot in use", "affected_person_agency",
   "Where a party has an interest in an operational-use process in which a lot bearing a safety-relevant disposition participates, a communication with that party as recipient must exist.",
   {"nodes": {"?party": node(), "?use": node(), "?lot": node("Portion of Processed Material"), "?d": node("disposition", safety_relevant=True)},
    "edges": [["?party","has_interest_in","?use"], ["?use","has_participant","?lot"], ["?lot","bearer_of","?d"]]},
   {"kind": "exists", "nodes": {"?c": node()}, "edges": [["?c","has_recipient","?party"]]},
   [{"objective": "OBJ-04", "rationale": "Persons with an interest in a process cannot participate in decisions about it unless addressed."}],
   {}, "Every interested party has been the recipient of a communication.")

rc("RC-10", "Regulatory notification of a safety-relevant nonconformance", "organizational_accountability",
   "Where a regulation prescribes a quality-management process and a safety-relevant nonconformance report exists, a communication delivering that report to a government organization must exist.",
   {"nodes": {"?reg": node("Process Regulation"), "?qms": node(), "?ncr": node("Report", kind="nonconformance_report", safety_relevant=True), "?lot": node("Portion of Processed Material")},
    "edges": [["?reg","prescribes","?qms"], ["?ncr","is_about","?lot"]]},
   {"kind": "exists", "nodes": {"?c": node(), "?gov": node("Government Organization")}, "edges": [["?c","has_input","?ncr"], ["?c","has_recipient","?gov"]]},
   [{"objective": "OBJ-03", "rationale": "The regulation makes notification of safety-relevant nonconformance an institutional obligation."}],
   {}, "A government organization has received a communication carrying the nonconformance report.")

rc("RC-11", "Decision informed by a preceding report communication", "organizational_accountability",
   "Where a communication carrying a nonconformance report precedes a decision act, the decision act must have that report as input.",
   {"nodes": {"?c": node(), "?rep": node("Report", kind="nonconformance_report"), "?dec": node(kind="decision")},
    "edges": [["?c","has_input","?rep"], ["?c","precedes","?dec"]]},
   {"kind": "exists", "nodes": {}, "edges": [["?dec","has_input","?rep"]]},
   [{"objective": "OBJ-05", "rationale": "A decision that follows a report but does not take it as input is made on unreliable information."}],
   {}, "The decision act has the communicated report as input.")

rc("RC-12", "Hold by the agent whose decision causes shipment after escalation", "safety_escalation",
   "Where a decision act by a person follows a communication carrying a nonconformance report and causes a shipment, a hold act by that person must precede the shipment.",
   {"nodes": {"?c": node(), "?rep": node("Report", kind="nonconformance_report"), "?dec": node(), "?p": node(), "?ship": node()},
    "edges": [["?c","has_input","?rep"], ["?c","precedes","?dec"], ["?dec","has_agent","?p"], ["?dec","is_cause_of","?ship"]]},
   {"kind": "exists", "nodes": {"?hold": node("Planned Act", kind="hold")}, "edges": [["?hold","has_agent","?p"], ["?hold","precedes","?ship"]]},
   [{"objective": "OBJ-02", "rationale": "The agent whose decision propagates a reported nonconformance is positioned to interrupt it."},
    {"objective": "OBJ-05", "rationale": "A hold records that the reported information reached the decision."}],
   {}, "A hold act by the deciding person precedes the shipment.")

rc("RC-13", "Interruption of a chain of effect reaching affected persons", "safety_escalation",
   "Where an act produced a nonconformance report, a communication carried it, a decision followed and caused a shipment whose lot participates in a use that affects a party, a hazard-control act on the lot must precede that use.",
   {"nodes": {"?a": node(), "?rep": node("Report", kind="nonconformance_report"), "?c": node(), "?dec": node(), "?ship": node(), "?lot": node("Portion of Processed Material"), "?use": node(), "?party": node()},
    "edges": [["?a","has_output","?rep"], ["?c","has_input","?rep"], ["?c","precedes","?dec"], ["?dec","is_cause_of","?ship"],
              ["?ship","has_participant","?lot"], ["?use","has_participant","?lot"], ["?use","affects","?party"]]},
   {"kind": "exists", "nodes": {"?ctrl": node("Planned Act", kind="hazard_control")}, "edges": [["?ctrl","has_participant","?lot"], ["?ctrl","precedes","?use"]]},
   [{"objective": "OBJ-02", "rationale": "The chain from reported nonconformance to affected persons is uninterrupted."}],
   {}, "A hazard-control act on the lot precedes the use that affects the party.")

rc("RC-14", "Containment of material bearing a safety-relevant disposition", "artifact_specification_conformance",
   "Where a lot bears a safety-relevant disposition and is a continuant part of an assembly, that assembly must not participate in an operational-use process.",
   {"nodes": {"?lot": node("Portion of Processed Material"), "?d": node("disposition", safety_relevant=True), "?assy": node()},
    "edges": [["?lot","bearer_of","?d"], ["?assy","has_continuant_part","?lot"]]},
   {"kind": "absent", "nodes": {"?use": node(kind="operational_use")}, "edges": [["?use","has_participant","?assy"]]},
   [{"objective": "OBJ-02", "rationale": "Material with an uncontrolled safety-relevant disposition must be contained, not placed in service."}],
   {}, "No operational-use process has the containing assembly as participant.")

doc = {"schema": "wrm-poc/reference_library/v1",
       "metadata_excluded_from_experiment": {"note": "Scenario-independent-style engineering reference conditions; no scenario IDs, no family ownership."},
       "pattern_language": {
         "nodes": "variable -> optional {type: exact CCO/BFO class label, attributes: exact-match attribute filters}",
         "edges": "[source_var, predicate_id, target_var]; all must be present in the filtered graph; node variables bind injectively",
         "constraints": "[lhs, op, rhs(, rhs2)] over bound entity attributes; ops: <, <=, ==, within",
         "prescribed.kind": "value_constraint | exists | absent (extension pattern evaluated per applicability binding)"},
       "reference_conditions": RC}
json.dump(doc, open(sys.argv[1], "w"), indent=1)
print(len(RC), "reference conditions")

# Expert review form — run `credited_run_3c60bcdf3c`

You are rating operational response workflows for a single frozen engineering case. Workflow labels are randomized; do not attempt to infer their origin. Rate each workflow 1–5 on each criterion and answer the comparative questions. This form is a future corroboration instrument and is not part of automatic success.

## Case (facts only)

A precision-machining supplier produces valve-body lots for brake actuators. Four successive bore-diameter measurements drift upward; the fourth exceeds the specification. A process engineer files a nonconformance report and emails it to the quality manager and plant manager. The quality manager acknowledges; the plant manager decides to continue production and ship the lot to the transit-authority customer with a certificate of conformance. The lot is installed and in service on buses carrying passengers. A regulation prescribes the supplier's quality-management process.

The fixed value disposition to be realized by the responder in every workflow is: **Courage** — The disposition of an agent to initiate or sustain a corrective act in the face of foreseeable personal or institutional cost when a discrepancy with a standard is present.

## Workflow A

Evidence presented to the responder (witness elements):

* Discrepancy `D-RC-02-1804fc59`: success when — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* Discrepancy `D-RC-02-ba1408e1`: success when — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* Discrepancy `D-RC-11-06b365f7`: success when — The decision act has the communicated report as input.
* Discrepancy `D-RC-12-81ab1efc`: success when — A hold act by the deciding person precedes the shipment.
* Discrepancy `D-RC-13-9e9b7a18`: success when — A hazard-control act on the lot precedes the use that affects the party.

Steps (evidence-preservation steps omitted):

* S009: propose_act — actor `P-ENG` create `has_participant` from `NEW-adj-1804fc` to `A-MILL` (resolve): establish the prescribed relation has_participant from NEW-adj-1804fc to A-MILL
* S010: propose_act — actor `P-INSP` create `precedes` from `ACT-M3` to `NEW-adj-1804fc` (resolve): establish the prescribed relation precedes from ACT-M3 to NEW-adj-1804fc
* S019: propose_act — actor `P-ENG` create `has_participant` from `NEW-adj-ba1408` to `A-MILL` (resolve): establish the prescribed relation has_participant from NEW-adj-ba1408 to A-MILL
* S020: propose_act — actor `P-INSP` create `precedes` from `ACT-M4` to `NEW-adj-ba1408` (resolve): establish the prescribed relation precedes from ACT-M4 to NEW-adj-ba1408
* S023: record_relation — actor `P-PM` create `has_input` from `ACT-DEC` to `NCR` (resolve): establish the prescribed relation has_input from ACT-DEC to NCR
* S028: propose_act — actor `P-PM` create `has_agent` from `NEW-hold-81ab1e` to `P-PM` (resolve): establish the prescribed relation has_agent from NEW-hold-81ab1e to P-PM
* S029: propose_act — actor `P-ENG` create `precedes` from `NEW-hold-81ab1e` to `ACT-SHIP` (resolve): establish the prescribed relation precedes from NEW-hold-81ab1e to ACT-SHIP
* S037: propose_act — actor `P-ENG` create `has_participant` from `NEW-ctrl-9e9b7a` to `LOT-4` (resolve): establish the prescribed relation has_participant from NEW-ctrl-9e9b7a to LOT-4
* S038: propose_act — actor `P-ENG` create `precedes` from `NEW-ctrl-9e9b7a` to `PROC-BRAKE` (resolve): establish the prescribed relation precedes from NEW-ctrl-9e9b7a to PROC-BRAKE

| criterion | rating 1–5 | comment |
|---|---|---|
| coherence | | |
| practical intelligibility | | |
| ethical plausibility | | |
| supported by its presented evidence | | |

## Workflow B

Evidence presented to the responder (witness elements):

* Discrepancy `D-RC-01-80f2d643`: success when — Every measurement of the prescribed quality lies within the specification bounds, or the artifact is segregated by a rework act.
* Discrepancy `D-RC-03-8a7079dc`: success when — A corrective-action act has the nonconformance report as input.
* Discrepancy `D-RC-04-9f7e9c12`: success when — The decision act that produced the directive has the nonconformance report as input.
* Discrepancy `D-RC-06-c00c8eb0`: success when — The recipient of the certificate has also received the nonconformance report.
* Discrepancy `D-RC-10-baae974f`: success when — A government organization has received a communication carrying the nonconformance report.
* Discrepancy `D-RC-11-06b365f7`: success when — The decision act has the communicated report as input.

Steps (evidence-preservation steps omitted):

* S004: rework_or_segregate — actor `P-ENG` create `has_participant` from `NEW-rework-80f2d6` to `LOT-4` (mitigate): bring the artifact's quality back within the prescribed bounds or segregate it
* S006: propose_act — actor `P-ENG` create `has_input` from `NEW-ca-8a7079` to `NCR` (resolve): establish the prescribed relation has_input from NEW-ca-8a7079 to NCR
* S010: record_relation — actor `P-ENG` create `has_input` from `ACT-DEC` to `NCR` (resolve): establish the prescribed relation has_input from ACT-DEC to NCR
* S015: propose_act — actor `P-ENG` create `has_input` from `NEW-c2-c00c8e` to `NCR` (resolve): establish the prescribed relation has_input from NEW-c2-c00c8e to NCR
* S016: propose_act — actor `P-ENG` create `has_recipient` from `NEW-c2-c00c8e` to `ORG-HTA` (resolve): establish the prescribed relation has_recipient from NEW-c2-c00c8e to ORG-HTA
* S019: propose_act — actor `P-ENG` create `has_input` from `NEW-c-baae97` to `NCR` (resolve): establish the prescribed relation has_input from NEW-c-baae97 to NCR
* S020: propose_act — actor `P-ENG` create `has_recipient` from `NEW-c-baae97` to `NEW-gov-baae97` (resolve): establish the prescribed relation has_recipient from NEW-c-baae97 to NEW-gov-baae97
* S023: record_relation — actor `P-ENG` create `has_input` from `ACT-DEC` to `NCR` (resolve): establish the prescribed relation has_input from ACT-DEC to NCR

| criterion | rating 1–5 | comment |
|---|---|---|
| coherence | | |
| practical intelligibility | | |
| ethical plausibility | | |
| supported by its presented evidence | | |

## Workflow C

Evidence presented to the responder (witness elements):

* Discrepancy `D-RC-02-1804fc59`: success when — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* Discrepancy `D-RC-02-ba1408e1`: success when — An act of artifact modification on the producing machine follows the last measuring act of the drifting sequence.
* Discrepancy `D-RC-05-5fdb3604`: success when — A hazard-control act on the lot precedes its operational use.
* Discrepancy `D-RC-14-5c650403`: success when — No operational-use process has the containing assembly as participant.

Steps (evidence-preservation steps omitted):

* S009: propose_act — actor `P-ENG` create `has_participant` from `NEW-adj-1804fc` to `A-MILL` (resolve): establish the prescribed relation has_participant from NEW-adj-1804fc to A-MILL
* S010: propose_act — actor `P-ENG` create `precedes` from `ACT-M3` to `NEW-adj-1804fc` (resolve): establish the prescribed relation precedes from ACT-M3 to NEW-adj-1804fc
* S019: propose_act — actor `P-ENG` create `has_participant` from `NEW-adj-ba1408` to `A-MILL` (resolve): establish the prescribed relation has_participant from NEW-adj-ba1408 to A-MILL
* S020: propose_act — actor `P-ENG` create `precedes` from `ACT-M4` to `NEW-adj-ba1408` (resolve): establish the prescribed relation precedes from ACT-M4 to NEW-adj-ba1408
* S023: propose_act — actor `P-ENG` create `has_participant` from `NEW-ctrl-5fdb36` to `LOT-4` (resolve): establish the prescribed relation has_participant from NEW-ctrl-5fdb36 to LOT-4
* S024: propose_act — actor `P-ENG` create `precedes` from `NEW-ctrl-5fdb36` to `PROC-BRAKE` (resolve): establish the prescribed relation precedes from NEW-ctrl-5fdb36 to PROC-BRAKE
* S027: withdraw — actor `P-ENG` attenuate `has_participant` from `PROC-BRAKE` to `A-ACT` (resolve): attenuate the offending relation has_participant from PROC-BRAKE to A-ACT

| criterion | rating 1–5 | comment |
|---|---|---|
| coherence | | |
| practical intelligibility | | |
| ethical plausibility | | |
| supported by its presented evidence | | |

## Workflow D

Evidence presented to the responder (witness elements):

* Discrepancy `D-RC-08-5f88093a`: success when — Each superior who received the escalation has performed an act with the escalating person as recipient.
* Discrepancy `D-RC-09-511c4f58`: success when — Every interested party has been the recipient of a communication.

Steps (evidence-preservation steps omitted):

* S006: propose_act — actor `P-PM` create `has_agent` from `NEW-r-5f8809` to `P-PM` (resolve): establish the prescribed relation has_agent from NEW-r-5f8809 to P-PM
* S007: propose_act — actor `P-ENG` create `has_recipient` from `NEW-r-5f8809` to `P-ENG` (resolve): establish the prescribed relation has_recipient from NEW-r-5f8809 to P-ENG
* S011: propose_act — actor `P-ENG` create `has_recipient` from `NEW-c-511c4f` to `AGG-PASS` (resolve): establish the prescribed relation has_recipient from NEW-c-511c4f to AGG-PASS

| criterion | rating 1–5 | comment |
|---|---|---|
| coherence | | |
| practical intelligibility | | |
| ethical plausibility | | |
| supported by its presented evidence | | |

## Comparative questions

1. Which pairs of workflows are substantively distinct in what they would change in the situation, and which are paraphrases of each other?

2. For each workflow, does realizing the fixed disposition (Courage) require redefining what Courage means? (yes/no, explain)

3. Which workflow would you expect a competent quality engineer to recognise as a legitimate response? Which would they reject, and why?

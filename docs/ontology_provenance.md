# Ontology provenance report

## Source

* **Common Core Ontologies (CCO) 2.0**, repository `CommonCoreOntology/CommonCoreOntologies`, file
  `src/cco-merged/CommonCoreOntologiesMerged.ttl`, commit `7a030e367a75126099a0117031c7e9ab289c2c2a` (2026-08-14), which imports
  **BFO 2020** (`src/cco-imports/bfo-core.ttl`). Cloned read-only during the build because no ontology files were supplied in the
  workspace (assumption A-02). Parsed with rdflib; 177 object properties indexed.
* Search order followed the ontology design methodology: CCO Extended Relation Ontology first, then the relevant CCO domain
  ontologies (Agent, Artifact, Information Entity, Event), then BFO. Every object property used in `data/scenario.json` is in the
  registry below with label, IRI, definition, domain, range and parent copied from the ontology file, not typed by hand
  (`scripts/build_predicate_registry.py`).
* No RDF/OWL object property was invented. Where CCO's domain or range is an anonymous union class, the registry says so.

## Object properties reused (20)

| id | label | IRI | domain → range | parent | primary MRC domain | source |
|---|---|---|---|---|---|---|
| `bearer_of` | bearer of | `http://purl.obolibrary.org/obo/BFO_0000196` | (anonymous union class) → specifically dependent continuant | specifically depended on by | physical_causal | BFO 2020 |
| `has_continuant_part` | has continuant part | `http://purl.obolibrary.org/obo/BFO_0000178` | continuant → continuant | (none) | physical_causal | BFO 2020 |
| `has_participant` | has participant | `http://purl.obolibrary.org/obo/BFO_0000057` | process → (anonymous union class) | (none) | physical_causal | BFO 2020 |
| `has_output` | has output | `https://www.commoncoreontologies.org/ont00001986` | process → (anonymous union class) | has participant | physical_causal | CCO 2.0 |
| `has_input` | has input | `https://www.commoncoreontologies.org/ont00001921` | process → (anonymous union class) | has participant | informational | CCO 2.0 |
| `is_cause_of` | is cause of | `https://www.commoncoreontologies.org/ont00001803` | process → process | (none) | physical_causal | CCO 2.0 |
| `precedes` | precedes | `http://purl.obolibrary.org/obo/BFO_0000063` | occurrent → occurrent | (none) | physical_causal | BFO 2020 |
| `realizes` | realizes | `http://purl.obolibrary.org/obo/BFO_0000055` | process → realizable entity | (none) | agentic | BFO 2020 |
| `has_agent` | has agent | `https://www.commoncoreontologies.org/ont00001833` | process → Agent | has participant | agentic | CCO 2.0 |
| `uses` | uses | `https://www.commoncoreontologies.org/ont00001813` | Agent → material entity | (none) | agentic | CCO 2.0 |
| `has_recipient` | has recipient | `https://www.commoncoreontologies.org/ont00001922` | Act of Communication → Agent | has participant | informational | CCO 2.0 |
| `is_about` | is about | `https://www.commoncoreontologies.org/ont00001808` | Information Content Entity → entity | (none) | informational | CCO 2.0 |
| `is_a_measurement_of` | is a measurement of | `https://www.commoncoreontologies.org/ont00001966` | Measurement Information Content Entity → entity | describes | informational | CCO 2.0 |
| `prescribes` | prescribes | `https://www.commoncoreontologies.org/ont00001942` | Prescriptive Information Content Entity → entity | is about | legal_institutional | CCO 2.0 |
| `has_organizational_context` | has organizational context | `https://www.commoncoreontologies.org/ont00001992` | role → Organization | (none) | legal_institutional | CCO 2.0 |
| `is_subordinate_role_to` | is subordinate role to | `https://www.commoncoreontologies.org/ont00001831` | role → role | (none) | legal_institutional | CCO 2.0 |
| `is_affiliated_with` | is affiliated with | `https://www.commoncoreontologies.org/ont00001939` | Agent → Agent | (none) | legal_institutional | CCO 2.0 |
| `affects` | affects | `https://www.commoncoreontologies.org/ont00001834` | process → (anonymous union class) | has participant | evaluative_experiential | CCO 2.0 |
| `has_interest_in` | has interest in | `https://www.commoncoreontologies.org/ont00001984` | Agent → process | (none) | evaluative_experiential | CCO 2.0 |
| `supervises` | supervises | `https://www.commoncoreontologies.org/ont00001943` | Person → Person | has affiliate | agentic | CCO 2.0 |

## Classes reused for entity typing

`cco:` = `https://www.commoncoreontologies.org/`, `obo:` = `http://purl.obolibrary.org/obo/`.

| class label | IRI | used for |
|---|---|---|
| Commercial Organization | cco:ont00000443 | supplier organization |
| Organization | cco:ont00001180 | customer organization |
| Government Organization | cco:ont00000408 | regulator |
| Person | cco:ont00001262 | engineer, managers, inspector |
| Group of Persons | cco:ont00000914 | passengers |
| Occupation Role | cco:ont00000984 | roles |
| Portion of Processed Material | cco:ont00001084 | valve body lots |
| quality | obo:BFO_0000019 | bore diameter |
| disposition | obo:BFO_0000016 | internal leakage disposition |
| Ratio Measurement Information Content Entity | cco:ont00001022 | bore measurements |
| Act of Measuring | cco:ont00000345 | inspections |
| Material Artifact | cco:ont00000995 | machining center, CMM, actuator assembly |
| Dimension Specification | cco:ont00001304 | bore specification |
| Report | cco:ont00002043 | nonconformance report |
| Prescriptive Information Content Entity | cco:ont00000965 | continuation directive |
| Certificate | cco:ont00002002 | certificate of conformance |
| Process Regulation | cco:ont00001324 | notification regulation |
| Plan | cco:ont00000974 | delivery schedule |
| Act of Manufacturing | cco:ont00001359 | machining |
| Act of Reporting | cco:ont00000151 | writing the report |
| Email Messaging | cco:ont00000492 | escalation email, reply |
| Planned Act | cco:ont00000228 | decision (limitation A-06) |
| Act of Cargo Transportation | cco:ont00000595 | shipment |
| Act of Communication | cco:ont00000402 | shipping notice |
| Act of Artifact Employment | cco:ont00000566 | in-service brake actuation |
| Act | cco:ont00000005 | quality management process |
| Act of Artifact Modification | cco:ont00000970 | proposed adjustment/rework acts (workflow proposals only) |

## Representation limitations (not invented properties)

* No CCO class for a decision act; `Planned Act` + attribute `kind=decision` (A-06).
* No CCO class for a nonconformance report; `Report` + attribute `kind=nonconformance_report` (A-05).
* Entity attributes (`value`, `lower`, `upper`, `kind`, `safety_relevant`, `asserts_conformance`, `sequence`) are prototype data
  properties, not ontology properties; implementation identifiers (`edge_id`, `family`, `step_id`) are not ontology properties.
* `is subordinate role to` is used with its CCO definition (a role whose bearer is addressed by regulations created by processes
  realizing the superior role); the scenario asserts it directly for the engineer→quality-manager→plant-manager chain and for the
  engineer→plant-manager pair.
* Considered and not used: `requires`/`permits`/`prohibits` (Process Regulation → process) because the regulated process type
  does not exist as an instance in the frozen graph; `prescribes` (their parent) was used instead.

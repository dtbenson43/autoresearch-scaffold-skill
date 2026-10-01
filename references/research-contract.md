# Research and artifact contracts

## Specify an executable scientific question

Define candidate input/output interfaces, units, primary metric and direction, hard constraints, baseline, data provenance, workload distribution, seeds, replication, aggregation, uncertainty, minimum worthwhile improvement, tie handling, resource limits and stopping rules. Separate exploration fixtures from held-out confirmation where feasible. State whether setup/training/index construction counts toward cost. Freeze evaluator and fixture hashes for an experiment. Changing the research contract creates a version boundary; do not rank incomparable measurements as if they share a benchmark.

For fuzzy matching, define whether this is edit-distance computation, threshold search, nearest-neighbor retrieval, or ranking. Specify Unicode normalization, string length distribution, corpus sizes, similarity definition, expected answers, recall/precision or exactness constraints, indexing amortization, warmup and memory limits. A fast trigram retriever and a distance calculator are not interchangeable interfaces.

For OCR extraction, define field schema, missing/null handling, normalization, document-level splits, provenance/line references, per-field accuracy and unacceptable error classes. Do not fabricate genuine labels or allow a candidate to read answers during inference. For simulation optimization, define initial conditions, seeds, fixed opponents/environment versions, success criteria and repeat counts.

## Artifact schemas

Generate actual JSON schemas or equally strict native validators; these field lists are requirements, not sufficient code validators. Validate types, enums, bounds, required fields, paths and referential integrity. Reject non-finite numeric values, omitted measurements and inconsistent Markdown/JSON claims. Markdown provides reasoning; JSON drives control. If they conflict, block the stage.

| Artifact | Required content |
| --- | --- |
| meta.json | experiment ID, parent candidate/research node, creation time, contract version/hash, selected exploration policy version, workspace manifest |
| hypothesis.json / .md | falsifiable claim, rationale, predicted metric changes, control comparison, mechanism, failure criterion, historical references |
| experiment.json / .md | independent variable, controls, data/splits, evaluator command ID, seeds/repeats, expected outputs, resource budget, candidate interface |
| verification.json / .md | approved/rejected enum, audited input hashes, issues with severity/evidence, scope and limitations |
| results.json | validity, candidate/baseline hashes, contract and evaluator provenance, raw observation references, repetitions, metrics with units, uncertainty, constraint checks, resource usage |
| analysis.json / .md | supported/unsupported/inconclusive claim outcome, measured effects, uncertainty, threats to validity, follow-up proposals |
| decision.json / .md | adopt/reject/inconclusive enum, evidence refs, parent/current revision, constraints, reason, proposed candidate manifest |
| history proposal | experiment ID, disposition, concise findings, cited artifact paths, current-best evidence, promising/failed/unexplored directions |

Auditor rejection is a normal result. A malformed auditor output is a failed stage. Require machine-readable approval plus audited hashes before execution. Analyst and selector cannot change measurement files. The controller computes comparable metric aggregates and constraint gates; agents interpret them.

## Dependencies and history

Declare exact stage inputs, outputs and validators in configuration. Pass a manifest of available documents to workers. Keep contexts bounded by retrieving relevant history, with links back to full records rather than replacing records with summaries. Preserve all explored branches, failed approaches, verifier issues, proposal rationale, snapshots, measurements, costs and decisions. Record search-parent relationships separately from chronology and event-log predecessors.

Make RESULTS.md a derived human-readable research memory with stable experiment links, provenance, current best, promising directions, failures and unknowns. Preserve prior versions and regenerate from canonical records if needed. Never use a summary as the sole measurement record.

If exploration-policy improvement is requested later, keep policy code/version separate from candidate code, evaluator and agent backend. Replay only stored branches with known outcomes. Hide outcomes until the replay policy selects a branch; charge historical costs and apply the same action interface. Use held-out discovery trees or prospective runs for confirmation. Unknown branches have unknown scores; history cannot predict experiments never performed. Label ordinary history-informed planning as such rather than claiming Dream-RSI reproduction.

# Runtime architecture and configurable workflow

Read protocol.md for the exact event envelope, legal operations and reducer projection. Its fixtures constrain shared replay semantics. Domain validators and workflow plans extend those semantics; a legal log is not proof of valid science.

## Profiles

Minimal default: BUILD combines proposal/implementation, MEASURE runs a fixed evaluator, DECIDE computes eligibility and records a disposition. Add a declared CONFIRM stage before adoption when scientifically required. A deterministic record operation need not call an agent. Audited profile: HYPOTHESIS, BUILD, VERIFY, MEASURE, ANALYZE, DECIDE, CONFIRM, RECORD, with configured edges for rejected audits and inconclusive measurements. These are examples, not mandatory role counts.

Persist the workflow graph, stage type (worker/evaluator/controller), inputs, outputs, validators, allowed result-to-next-stage mapping and session policy before starting experiments. A worker's suggested next stage is never authority; controller code chooses from validated outcomes. One step attempts exactly one configured stage, then exits. Recovery bookkeeping and new-experiment allocation can precede that stage; they must not secretly execute additional stages.

Separate initialization from experimentation. Initialize only after baseline/oracle readiness checks, or explicitly mark a test project mock. Check budgets/readiness before opening a new experiment. Define how failed/blocked experiments are closed, and retain unsuccessful attempts. No implicit adoption on exhaustion. Log structured IDs separately from human-readable slugs.

## Publication: journal is authority

Use a project-wide single-writer lock across replay, attempt, artifact publication and commit. The controller owns journal, canonical artifacts and candidate views. Use OS locking or atomic acquisition with owner identity; do not steal a live owner's lock just because it is old. Stop child processes before releasing ownership after failure. Bound each invocation; preserve separate stdout/stderr logs.

Before appending a completed event: validate stage outputs, publish immutable artifacts/manifests under safe paths, flush files and containing directories where supported, verify their hashes, and recheck incumbent/evidence/budget gates. Then append the complete newline-terminated event and durably flush the journal. That completed record is the logical commit point. Only after it may current-candidate pointers and RESULTS.md be refreshed. The journal's durability depends on the filesystem/platform; document and test actual guarantees rather than promising identical power-loss behavior everywhere.

| Interruption point | Recovery |
| --- | --- |
| Before completed record | Previous committed state wins; orphan artifacts never imply success; reconcile/interrupt the pending attempt and retry under budget |
| Complete committed record, stale pointer or summary | Replay adopts the committed state; rebuild views idempotently without rerunning the agent or evaluation |
| Unterminated final record | Treat as uncommitted even if its JSON parses; preserve bytes before explicit locked tail repair |
| Invalid complete record or middle corruption | Fail closed; no silent skipping or automatic scientific advancement |

Read-only status reports journal-derived state, pending attempt and stale views without changing files. `step` or explicit recovery may rebuild views. After a write/flush error, fail uncertain and reconcile the existing journal before another append; never append a contradictory failed event blindly after a potentially committed completion. The protocol reader rejects an unterminated tail; it does not itself repair files.

Use immutable artifact references in events. Before resuming after a crash, check their existence and hashes. A completed event with missing evidence is an integrity error, not permission to rerun and overwrite it. Record operator recovery explicitly. Repeated retries may repeat subprocess side effects: require idempotent evaluators or explicit reconciliation for effects outside the project.

## Revisions and invalidation

Use the protocol's exact build revision rules. A build attempt gets a new revision; failed attempts are not reused. Freeze candidate, plan and evaluator references before measurement. A repair invalidates all downstream approval/results tied to the old revision; additional measurement batches keep the revision unchanged. Retain old artifacts rather than overwriting them. Contract/evaluator changes require a new cohort and baseline evidence, not merely another candidate revision.

Promotion requires a controller-computed eligible decision for the exact revision, required confirmation evidence, current-parent match and real-mode provenance for real projects. A mock project may simulate promotion only within its own isolated namespace. The protocol checks configured promotion outcomes, completed-build state, mode and lineage; domain code independently recomputes the gates from immutable evidence. Never trust a worker-supplied eligibility boolean.

## Interfaces and compatibility

Expose describe, status, step, continue, history, inspect, validate and doctor; add domain-specific commands and initialization/recovery commands as needed. Read-only replay accepts a JSONL file and produces the protocol projection for fixture checks. Commands resolve project-relative paths independently of cwd. Spawn executable/argument arrays without shell interpolation. Reject unexpected output files, path escapes and unsafe imports.

Document exit codes distinguishing success, stopped, blocked, busy and failed. If supporting `while research step`, stop must terminate the loop rather than spin. Emit structured status on stdout and diagnostics on stderr. Respect per-stage and overall budgets, including retries and confirmation reservations.

Copy the protocol version and conformance fixtures into generated projects. Run the checker against each generated implementation. Also test lock contention, timeouts, crash injection before/after commit, artifact integrity, budget persistence, mock isolation, invocation from another cwd and status nonmutation. Fixtures cover semantic replay; integration tests cover mechanisms. Preserve old schema readers or perform explicit backup-preserving migrations with replay equivalence checks. Do not label a changed schema with the old version.

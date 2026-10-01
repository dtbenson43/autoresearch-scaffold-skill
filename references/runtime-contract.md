# Runtime contract

## State semantics

Use this stage order; each invocation attempts only the next eligible stage:

| Stage | Worker | Required outcome | Next |
| --- | --- | --- | --- |
| HYPOTHESIS | planner | hypothesis.md and hypothesis.json | BUILD |
| BUILD | builder | experiment.md, experiment.json, workspace snapshot | VERIFY |
| VERIFY | auditor | verification.md and verification.json | RUN if approved; BUILD if rejected |
| RUN | controller evaluator | raw observations and results.json | ANALYZE |
| ANALYZE | analyst | analysis.md and analysis.json | DECIDE |
| DECIDE | selector | decision.md and decision.json | UPDATE |
| UPDATE | historian + controller | history proposal, validated RESULTS.md update and optional promotion | READY |

Initial state and READY select HYPOTHESIS. Allocate the experiment ID and immutable parent-candidate snapshot within that stage's transaction, so retry reuses the same ID. READY is the outcome of UPDATE, not a hidden extra agent call. Check stop conditions before opening another experiment. UPDATE has one historian session; deterministic import and promotion are controller operations, not extra agent roles. Do not call promotion a proven scientific improvement solely because a selector says adopt.

Persist build revision numbers. A rejected verification completes the verification stage but does not authorize RUN. Bind approved verification to exact workspace, plan, evaluator, fixture and contract hashes; rebuilding invalidates prior approval. Exhausted repair budgets produce a blocked/terminal experiment, never permission to run invalid work. Explicitly record closure before starting another experiment.

## Event schema and replay

Use UTF-8 JSONL, one controller event per line, with fields:

```json
{"schemaVersion":1,"seq":12,"id":"event-unique","previousId":"event-11","timestamp":"2026-10-01T13:00:00Z","researchId":"research-unique","experimentId":"007","stage":"BUILD","attemptId":"attempt-unique","attempt":2,"buildRevision":2,"type":"completed","contractHash":"sha256:...","artifacts":[{"path":"experiments/007/attempts/BUILD-2/experiment.json","sha256":"..."}],"outcome":{"nextStage":"VERIFY"}}
```

Define started, completed, failed, interrupted, blocked, stopped, and recovery events in RUNTIME.md. Link each terminal attempt event to exactly one started event. Enforce monotonic sequence, unique IDs, legal transitions, matching experiment/attempt IDs, contract versions, and required hashes. Reject out-of-order or duplicate completions. A completion must contain a validated stage-specific outcome; arbitrary `nextStage` text is not authority. Replay the whole log through the transition reducer. Derived state caches are disposable and cannot override the log.

Write started before invoking work; write completed only after validated artifacts have been atomically published and flushed. Record backend errors/timeouts as failed, keeping the state eligible for a bounded retry. Keep stdout/stderr in logs/<experiment>/<stage>/<attempt>/, not mixed into JSONL. Preserve attempt artifacts, including rejected builds and failed output. A result of zero or missing metric is not a generic success.

Treat only a final unterminated partial record as a possible torn append. Preserve its bytes in a recovery artifact before truncating to the last verified boundary under the lock; append a recovery event describing the repair. Fail closed for invalid newline-terminated JSON, schema violations, or corruption in the middle. Do not quietly skip bad records. Hashes detect accidental changes; they do not provide authenticity against a process that can rewrite the entire log.

## Single writer and recovery

Hold a project-wide exclusive controller lock across replay, work, publication and completion. Use an OS lock or atomic lock acquisition with owner identity and documented stale recovery. Never steal a lock merely because it is old while the owner may still be alive. A second invocation returns busy without launching an agent. Account for child process termination before releasing a failed attempt's lock.

Use an attempt-specific staging directory and subprocess timeouts. Avoid shell interpolation; spawn executable plus argument array. Bound wall time, stage attempts, verification repairs, experiment count, and backend usage where measurable. Include explicit exit codes for success, busy, stopped, blocked, and failed so a loop cannot spin forever on stop. Document them; use nonzero stop with a machine-readable reason if supporting `while research step`.

A started event without a terminal event is interrupted, not completed. After acquiring the lock, reconcile staged outputs and committed manifests. Do not infer success just from a file's existence. Retry with a new attempt ID unless a validated durable transaction manifest proves the previous operation committed. Record interrupted work before retry; keep earlier outputs. Do not promise exactly-once external subprocess effects. Make evaluator retry safe or block for explicit recovery if it has irreversible side effects.

## Publication and candidate promotion

Store each candidate as an immutable content-addressed revision, with a manifest and scientific evaluation provenance. Keep a controller-owned atomic current-candidate pointer. Record parent revision, proposal hash, contract/fixture/evaluator hashes and decision provenance. Permit branching from an explicit historical parent, but promotion must compare against the current revision and cannot silently overwrite a newer winner.

For UPDATE, stage the history summary and candidate revision, validate deterministic constraints and references, then persist a transaction manifest before replacing pointers/RESULTS.md. Reconcile interrupted commits using that manifest and hashes, and only then append completion. Re-running UPDATE must not create duplicate history entries or repeat promotion. Preserve the previous pointer/history for recovery. If local filesystem semantics cannot safely implement this protocol, choose a transactional store or an explicitly documented compatible commit mechanism.

Never let an agent copy arbitrary workspace files into the canonical candidate. Import only the declared candidate interface, reject path traversal/symlinks escaping the staging root, and re-evaluate the exact imported revision when required. Store adoption evidence independently of agent prose. A deterministic gate can veto adopt when constraints fail, uncertainty is excessive, provenance is stale, or budgets prohibit final verification.

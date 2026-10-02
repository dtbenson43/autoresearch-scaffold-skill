# Portable conformance protocol v2

This is a small, exact wire protocol and deterministic replay oracle, **not a research controller**. A generated runtime may use a richer internal schema, but must export this projection and a replay command to check these vectors. Do not describe passing these vectors as proving scientific correctness or runtime safety.

## Encoding and commit boundary

A log is UTF-8 JSON Lines. Every record, including the final record, ends with LF. Blank lines, duplicate JSON keys, NaN/Infinity, unknown fields, unknown versions, malformed records, and a nonterminated tail are errors. Sequence numbers are integers starting at 1 with no gaps. IDs are nonempty strings; event IDs, attempt IDs and experiment IDs cannot be reused within a log. Booleans are not integers.

The writer holds an exclusive writer lock, stages and validates immutable artifacts, flushes them and makes their paths durable **before** appending a referencing completion. It appends one serialized event plus LF and flushes the event log to durable storage. A stage result (including a promotion) commits at the **durable newline-terminated `stage_completed` record**. A pre-commit artifact is an unreferenced orphan; a committed artifact must remain available. Merely staging artifacts or replacing a candidate pointer does not commit a result. A reader can check termination but cannot prove fsync occurred.

Current-candidate pointers, result summaries, indexes, and human-readable history are derived views. Rebuild them from committed events after a crash. Promotion is embedded in the completion record, so there is no independent pointer/history transaction to guess at. If a committed completion exists, never rerun that attempt. If only a start exists, the controller first reconciles the worker, then records `stage_interrupted` before a fresh attempt. A reducer does not infer an interruption from elapsed time. Failure/interruption keeps the current stage and revision, and consumes the attempt ID.

Reject a torn tail during ordinary replay. A controller's explicitly documented repair procedure may preserve the original log, verify the complete prefix, and remove only the incomplete trailing bytes under its writer lock; it must never discard a malformed newline-terminated record. This oracle does not mutate or repair logs.

## Exact event schemas

All events contain `v: 2`, `seq` (positive integer), `id` (event ID), and `type`. The table lists all additional required keys; there are no optional or extension keys.

| Type | Additional keys | Meaning |
| --- | --- | --- |
| `initialized` | `workflow`, `baseline` | Exactly once, first event. Establish immutable workflow and explicit initial candidate. |
| `experiment_started` | `experimentId`, `candidateId`, `parentId`, `mode` | Open one experiment against current candidate. Candidate ID must be new, mode is `real` or `mock`. |
| `stage_started` | `experimentId`, `stage`, `attemptId`, `buildRevision` | Begin exactly the current stage, with fresh attempt ID; allocate the next revision if this is the build stage. |
| `stage_completed` | `experimentId`, `stage`, `attemptId`, `buildRevision`, `outcome`, `nextStage`, `artifacts`, `promote` | Match the active attempt, validate edge, commit output and optionally promotion. |
| `stage_failed` | `experimentId`, `stage`, `attemptId`, `buildRevision`, `reason` | Match active attempt; record nonempty failure reason; stage and revision stay unchanged. |
| `stage_interrupted` | Same as `stage_failed` | Explicit recovery event after reconciling an unfinished attempt. |
| `experiment_closed` | `experimentId`, `outcome` | Close only after a terminal completion, with that completion's outcome. |

`baseline` is exactly `{ "id": "baseline-id", "mode": "real" }`, or mode `mock`. Baseline has no implied experiment or revision. `parentId` must match the current candidate when the experiment starts and again at promotion. This single-active-experiment protocol intentionally does not model concurrent research branches; the stale-parent fixture rejects stale input at experiment creation.

`workflow` is exactly:

```json
{
  "initialStage": "build",
  "buildStage": "build",
  "edges": {
    "build": {"built": "verify"},
    "verify": {"pass": "measure", "reject": "build"},
    "measure": {"inconclusive": "measure", "accept": null, "reject": null}
  },
  "promotionOutcomes": ["accept"]
}
```

Stage and outcome names are configurable nonempty strings. Every stage has at least one outcome. All non-null edge targets and both designated stages must exist. The example is a fixture configuration, not a required universal pipeline. Each completion explicitly supplies `outcome` and `nextStage`, and the latter must equal the configured edge target. Null means terminal, after which no stage may start. A terminal outcome may close without promotion. New experiments require the previous one to close. Failure/interruption is not an outcome edge and cannot advance stages.

`buildRevision` starts at zero for every experiment. Starting `buildStage` allocates the next integer revision immediately; other stage starts carry the current revision. Completion, failure and interruption must carry that attempt's allocated revision unchanged. A failed or interrupted build's revision is never reused: the retry allocates the next one. `builtRevision` is null until a build completes and then records the most recently committed build revision; promotion requires a completed build at the current revision. A completed build can also promote directly in a single-stage workflow. Artifacts from older revisions remain immutable; runtime stage-input contracts must select the proper revision's artifacts.

`artifacts` is an array, possibly empty, of exact `{ "path": "experiments/x1/a1/output.json", "sha256": "64 lowercase hex characters" }` descriptors. Paths are relative, use `/`, and contain no empty, `.` or `..` components or backslashes. A path cannot be reused across completions in the log. The oracle validates descriptors and uniqueness, **not file existence, filesystem containment, contents, hashes, or durability**. The runtime must perform those checks before commit, resolve symlinks safely, and use platform-safe artifact names.

`promote` is a JSON boolean. If true, the outcome must be in `promotionOutcomes`, the edge must be terminal, at least one build must have completed, the experiment must not already have promoted, and the parent must still be current. A mock candidate cannot replace a real candidate. Real-to-real, real-to-mock-baseline, and mock-to-mock promotion are permitted by this structural protocol; the research contract can impose stricter rules. Mock evidence never establishes real scientific improvement.

## State and invocation

The replay command prints one JSON object to stdout on success and exits zero. On rejection it exits nonzero and emits a diagnostic on stderr. It performs no writes. Object key order is irrelevant; array order is significant. `schemaVersion`, `seq`, `workflow`, `currentCandidate`, `experiment`, `history`, `eventIds`, `attemptIds`, and `experimentIds` are the exact top-level state keys. An open experiment retains its IDs, mode, current `stage`, `buildRevision`, `builtRevision`, `activeAttempt`, `lastOutcome`, `promoted` flag, and committed `artifacts`. Closing moves that record to `history` and sets `experiment` to null. The full log remains the authority for failed attempts and artifact provenance.

```sh
python scripts/reference_reducer.py references/fixtures/successful_promotion.jsonl
python scripts/check_conformance.py
python scripts/check_conformance.py --command python scripts/reference_reducer.py
```

For generated runtimes, replace the command after `--command` with the runtime's **read-only portable-v2 replay adapter**; the harness appends each fixture path as its final argument. It compares accepted states with frozen expected JSON and requires nonzero exit for negative cases. No shell interpolation or package dependency is required. A replay adapter alone does not establish controller conformance: also test logs emitted by real controller operations and the implementation's filesystem/process boundaries.

## Fixture scope

The 25 bundled vectors cover initialization, promotion and close, promotion replay before derived close/history updates, verifier rejection and second build, inconclusive measurement and remeasurement, failure retry, explicit interruption retry, retained active attempt, stale initial parent, completion without start, illegal edge, wrong revision, reused attempt ID, premature close, mock-over-real promotion, duplicate event ID, invalid sequence, incomplete JSON tail, missing final LF, malformed complete line, duplicate JSON keys, mock-to-mock promotion, unknown event fields, unsupported version, and attempted promotion-stage entry after a failed build. The failed-build case checks that failure cannot advance to a promotion stage; it does not bypass ordering to isolate the built-revision guard.

Positive fixtures have frozen expected states; negative fixtures assert rejection, not a particular diagnostic string. Their hashes are placeholders and their paths do not claim real artifacts. They do **not** test physical crash durability, operating-system locks, concurrent writer exclusion, actual artifact validation, subprocess isolation, agent freshness, evaluator integrity, budgets, contract migrations, or scientific validity. Those require generated-runtime tests. Never label these static replay cases as lock, crash, sandbox, or live-backend tests.

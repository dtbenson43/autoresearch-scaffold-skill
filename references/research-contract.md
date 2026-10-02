# Scientific, measurement and budget contract

## Oracle and initialization

Specify the function being optimized, candidate interface, valid inputs/outputs, workload and constraints before choosing a search strategy. Record how expected answers are established independently of the candidate. Suitable sources include manually adjudicated labels, proven definitions with a separate reference implementation, trusted external measurements, or exhaustive enumeration on a bounded domain. A reference can be buggy: cross-check hand-worked edge cases and properties. A baseline's outputs alone establish compatibility, not truth. For inherently subjective tasks, define a blinded rating procedure and uncertainty rather than claiming objective correctness.

Before the first experiment, record an initialization report with oracle provenance, fixture hashes/split policy, evaluator version, successful known-correct cases and failures of deliberately defective candidates. Include plausible defects: constant outputs, dropped edge cases, wrong normalization, label access, or shortcuts that change the specified task. Some leakage defenses require isolation or inspection rather than output tests. Freeze evaluator and scoring rules after validation. Changing them starts a new comparison cohort and requires remeasuring the incumbent.

Construct or import a baseline through an explicit setup operation with its own provenance. Test correctness before measuring speed. If no baseline exists, record baseline construction as setup rather than a discovery. Empty fixtures, unavailable authentic labels or unverified backends block scientific-ready status. Synthetic examples can test logic; they cannot establish real-world extraction accuracy.

## Measurement plan

Record primary metric/direction/units, hard constraints, minimum useful effect, observation unit, nuisance variables, seeds, replication, aggregation, uncertainty method, stopping rules, setup costs and confirmation budget. Distinguish repeated timing samples of one input from independent examples or independent process runs. More inner-loop iterations do not create more independent evidence.

| Domain | Minimum methodological choices |
| --- | --- |
| Function benchmark | Correctness first; warmup policy for JIT/caches, timer resolution, sufficiently long timed blocks, output consumption to prevent dead-work artifacts, interleaved/randomized paired baseline/candidate blocks, startup/index-build accounting, representative size distributions, fresh-process repeats where appropriate |
| OCR/prompt extraction | Authentic adjudicated labels, explicit missing/null and normalization rules, document/group splits to prevent template/person leakage, per-field and document metrics, provenance evidence, unacceptable-error constraints, fixed model/preprocessor/inference settings |
| Simulation | Frozen environment/opponents, independent seeds, paired seed comparisons where appropriate, distribution of outcomes and failure rates, fixed horizon and termination rules |

Estimate measurement variation with a bounded baseline-versus-baseline pilot. Use it to choose measurement duration and a fixed sample plan or a justified sequential procedure. There is no universal run count. State the assumptions behind confidence intervals and power/sample-size estimates. For paired observations use paired differences or ratios; bootstrap at the independent unit, not at arbitrary inner-loop iterations. If there are too few independent units or violations of assumptions, report limited evidence rather than manufactured precision.

Choose a primary statistic before inspecting candidate outcomes. Treat ties and below-useful-threshold effects explicitly. Account for repeated candidate selection: exploration identifies promising changes, not confirmed winners. Reserve an untouched confirmation set or fresh confirmation runs; apply a declared familywise/false-discovery or sequential policy when making repeated inferential claims. Repeatedly checking the same holdout and changing candidates in response makes it exploration data. Track exposure and refresh/retire it as declared.

Inconclusive results may trigger another batch only under a predeclared maximum and inference procedure. Do not repeatedly compute ordinary fixed-sample intervals and stop on the first favorable result. A simple safe default is fixed exploratory measurement plus one separately scheduled fixed-size confirmation of the selected candidate. If budget cannot resolve the effect, retain the incumbent and close as inconclusive.

## Scientific outcomes and invalidation

| Outcome | Action | Evidence retained/invalidation |
| --- | --- | --- |
| Incorrect implementation | BUILD a new revision or reject | Retain failing cases; invalidate candidate-dependent approval and measurements |
| Invalid design | Repair plan/evaluator through controlled revision | Retain audit; invalidate affected observations; evaluator changes require a new cohort and incumbent remeasurement |
| Inconclusive | MEASURE same frozen revision or close | Preserve all valid batches; follow predeclared stopping policy |
| Supported improvement | CONFIRM if required, then deterministic adoption gate | Confirm exact evaluated snapshot and constraints |
| No useful improvement | Close rejected | Preserve measurements and reasons |

An infrastructure timeout is a failed attempt, not a scientific failure or a zero score. Auditor rejection is a valid audit result, not a malformed output. Invalid measurements are excluded only by predeclared rules, with their raw data and exclusion reason retained.

## Evaluated unit and hashes

Record candidate source/data, dependency lockfiles or exact dependency versions, launch arguments, preprocessing, relevant environment settings, runtime/model identity and inference parameters, evaluator and fixtures. Hash a manifest of declared files with normalized relative POSIX paths sorted by path and SHA-256 of exact bytes. Reject escaped paths and symlinks outside the allowed root. Exclude logs, timestamps, generated views and the manifest's own digest. Serialize hash manifests with a documented canonical encoding; avoid float ambiguity by using strings for decimal configuration values. Hash the evaluation contract separately from mutable budget counters and derived state.

Record hardware/runtime/backend identity even when it cannot be snapshotted; label the reproducibility limit. Matching file hashes do not prove an external service or nondeterministic model behaves identically. Measurements must bind to the full evaluated unit, including the baseline and environment cohort. Validate the exact candidate import before promotion; if import changes evaluated bytes or dependencies, re-evaluate.

## Artifacts and deterministic gates

Generate strict JSON schemas/native validators for initialization, proposal, plan, audit where used, results, decision and publication. Required shared fields: experiment ID, parent revision, build revision, contract/evaluator/fixture/environment references, candidate snapshot, artifact hashes, mode (mock/real), invocation/session IDs and costs. Results include raw-observation references, sample units/counts, statistics, uncertainty, exclusions, constraint checks and measurement batch ID. Decisions reference evidence and encode adopt/reject/inconclusive, not agent confidence as a substitute for measurement.

Controller code computes metric aggregates, correctness/constraint checks and eligibility. Agents can propose interpretations and recommend decisions; they cannot fabricate measurement fields or override a failed gate. Confirmation must be an independent evaluator invocation with protected inputs as declared; a different language-model session alone does not establish independence.

Render factual Markdown tables/summaries from JSON. Keep rationale separate. A machine validator checks types, finite values, units, hashes and cross-references; semantic prose review is advisory unless an explicit review stage is configured. Keep full attempt history and parent relationships. RESULTS.md is a disposable view, never the sole evidence record.

## Cost and stopping policy

Set limits for wall time, experiments, build repairs, measurement batches, agent calls, tokens and monetary spend where measurable. Declare model/provider price assumptions and distinguish actual, estimated and unknown costs. Unknown is never zero. Where token/spend telemetry is unavailable, enforce hard call/time limits and disclose that a dollar cap cannot be guaranteed. Do not invent current prices.

Estimate total cost as initialization + expected experiments × (role calls + repairs + measurement batches) + reserved confirmation. Before admitting an operation reserve its configured worst-case or conservative bounded cost; reconcile actual usage afterward. Persist reservations/usage before another invocation can spend the same allocation. Charge interrupted work conservatively until reconciled. Use backend token/time limits when supported. Do not launch if remaining budget cannot cover mandatory confirmation. On exhaustion commit a stopped/blocked outcome, retain the incumbent and provide the reason; an operator may explicitly revise the budget.

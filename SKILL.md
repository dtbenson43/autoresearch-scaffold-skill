---
name: autoresearch
description: Generate or reconstruct a domain-specific autoresearch folder with a local stepwise CLI, validated measurement methods, configurable agent workflows, cost limits, and durable experiment history. Use for requests to set up autoresearch, scaffold an experiment harness, or rebuild its runtime for another environment. Generates the research runtime rather than running an indefinite loop.
---

# Autoresearch

Translate the research objective and available environment into a small, self-contained research runtime. Use durable design documents as the regeneration source. Select Node, Python, PowerShell, shell or another suitable installed runtime; do not ship one universal evaluator. This is version 2 of the scaffold contract.

Read [research-contract.md](references/research-contract.md) first, then [runtime-contract.md](references/runtime-contract.md), [protocol.md](references/protocol.md), and [agent-adapters.md](references/agent-adapters.md). Consult [foundations.md](references/foundations.md) for attribution and limits. Use the executable [reference reducer](scripts/reference_reducer.py), [conformance checker](scripts/check_conformance.py), and [fixture manifest](references/fixtures/manifest.json) as compatibility anchors, not as a complete runtime or proof of scientific validity.

## Preserve the boundaries; choose the workflow

Require independent measurement authority, controller-enforced adoption gates, durable provenance and honest results. Workers cannot change authoritative observations, evaluation rules during an experiment, or the current candidate. Never fabricate evidence or turn missing data into a score. Keep research records recoverable with the commit semantics in the runtime contract.

Select minimal mode by default for a bounded, inexpensive optimization: BUILD (proposal and implementation), MEASURE (fixed evaluator), DECIDE (deterministic gate and record). Add confirmation as a separate measurement stage when required. Select audited mode for complex methodology, expensive evaluations, or an explicit user preference: HYPOTHESIS, BUILD, VERIFY, MEASURE, ANALYZE, DECIDE, CONFIRM, RECORD, with declared repair and remeasurement edges. Omit unnecessary stages, not evidence requirements. Explain the choice and expected cost in RESEARCH.md. Each `research step` attempts one configured stage; combined roles must be declared in that stage, never hidden cascades of agent calls.

## Establish scientific readiness before runtime generation

Inspect the requested folder; preserve existing work and history. Resolve the objective, candidate interface, workload, correctness oracle, baseline, minimum useful improvement, constraints, observation units, measurement procedure and confirmation rule. Ask only for unresolved choices that materially affect meaning. Do not invent business thresholds or authentic labels.

Write the oracle provenance and evaluator validation plan before implementing the scorer. Require known-correct cases, independently justified expected outputs, deliberately incorrect candidates and edge cases. A baseline is a comparator, not automatically a correctness oracle. Properties and differential checks supplement an oracle; document their limits. If no trustworthy oracle exists, label results exploratory and disallow claims of verified correctness.

Define initialization: validate the evaluator, construct or import the baseline, snapshot its full evaluated environment, measure it and record readiness evidence before the first research experiment. Missing genuine data or a backend permits a scaffold and isolated mock tests, not scientific-ready status. Follow the research contract for sampling, noise, adaptive comparisons and confirmation.

## Discover the environment and write durable specifications

Use bounded read-only probes for OS, runtimes, locking/atomic publication support, dependencies, data, Git and agent CLIs. Inspect actual help/version before choosing flags; do not assume `gh copilot` is the available Copilot command. Prefer installed capabilities and avoid unnecessary downloads. Without an available backend, configure it as blocked and provide explicit test-only mock mode.

Create RESEARCH.md (scientific and budget contract), RUNTIME.md (protocol, workflow, schemas, recovery and commands), ENVIRONMENT.md, AGENTS.md, research.config.json, project-local `research` or a platform-appropriate launcher, runtime/, prompts/, experiments/, candidate revisions, fixtures/ when applicable, logs/, research.log.jsonl and derived RESULTS.md. Do not globally link the CLI. Resolve paths from the project root independently of caller cwd.

Specify the evaluated unit, dependency and environment manifests, digest rules, input/output schemas, workflow edges, output validators, session policies and permissions. Keep JSON authoritative for machine decisions. Render factual Markdown from JSON; free-form rationale may be preserved without pretending semantic agreement is mechanically provable. Design documents plus copied protocol fixtures must suffice to regenerate the runtime without this skill installation.

## Implement and verify

Implement describe, status, step, continue (alias), history, inspect, validate, doctor, and read-only replay for conformance. Initialization and recovery may have explicit commands. Status must replay authoritative events without repairing files. Do not silently replay old records under a new schema. Retain v1 support or provide an explicit migration with backup and equivalence checks.

Implement one writer, bounded subprocesses, strict output import, immutable artifacts, journal-first promotion and derived views. Separate implementation failure, invalid design, inconclusive measurement, supported improvement and rejection. Add measurement batches only under the predeclared sampling/stopping procedure; do not revise a frozen candidate during remeasurement.

Run the bundled fixture suite against the generated reducer, not only the bundled reference reducer. Run generated runtime integration checks for missing/malformed output, lock contention, timeout, interruption around the commit point, stale parent, budget exhaustion, mock/real separation, read-only status and invocation from another cwd. A passing reducer suite covers replay only, not filesystem or subprocess behavior.

Also execute a small real domain evaluation: a checked baseline, an intentionally defective candidate that must be rejected, and a correct alternative measured by the fixed evaluator. Require confirmation in a separate evaluator invocation when the adoption policy calls for it; agent review alone is not independent evidence. Do not require an improvement to exist. Report inconclusive findings honestly. Use mock observations only to test control-flow paths that real data did not exercise, clearly segregated from real results.

At handoff report runtime and backend readiness, oracle/evaluator checks, conformance and integration results, costs/remaining limits and exact inspect/step commands. Do not start unattended research unless requested.

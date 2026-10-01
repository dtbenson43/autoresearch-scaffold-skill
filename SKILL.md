---
name: autoresearch
description: Scaffold or reconstruct a portable autoresearch folder with a custom local CLI, event-sourced state machine, fresh specialized headless agent sessions, objective evaluation, and durable experiment history. Use for requests such as set up autoresearch in a folder, generate a research harness, or rebuild its runtime for a different environment. The skill generates the runtime; it does not itself run an indefinite research loop.
---

# Autoresearch

Compile the research objective, environment capabilities, and durable design contracts into a self-contained experimental runtime. Preserve semantics across Node, Python, PowerShell, shell, or another suitable installed runtime. Generate domain-specific tooling rather than imposing one universal benchmark.

Read [runtime-contract.md](references/runtime-contract.md), [research-contract.md](references/research-contract.md), and [agent-adapters.md](references/agent-adapters.md) before generating code. Read [foundations.md](references/foundations.md) when designing history or explaining the paper connections. Treat the runtime contract as mandatory unless the user explicitly changes it; document any such change.

## Establish the target

Use the supplied folder and objective. Inspect existing contents before writing. Preserve unrelated files and all existing research records. Infer routine choices from context; ask only for information that changes the experiment's meaning, such as what matching accuracy means or whether training compute is available. Do not silently invent labels, business requirements, or a success threshold. Record unresolved assumptions and block scientific execution until required ones are resolved.

Discover installed runtimes, OS/shell, executable permissions, Git, data access, dependencies, and available agent CLIs using bounded read-only probes. Inspect actual CLI help/version before selecting arguments. Do not assume `gh copilot` is the modern Copilot executable. Do not install packages, download models, or require network access merely to scaffold when existing tools suffice.

Select the simplest runtime that reliably handles JSON, subprocess argument arrays, locking, atomic writes, hashing, and durable append. Use shell only when these properties can be implemented and verified with available utilities. Record capabilities and the selected implementation in ENVIRONMENT.md. If no usable agent backend exists, generate a mock backend and explicit blocked real-backend configuration; never substitute fabricated research results.

## Write the durable design first

Create RESEARCH.md defining the question, candidate interface, evaluation protocol, metrics, constraints, adoption rule, budgets, and stopping conditions. Create RUNTIME.md describing state/event schemas, stage dependencies, artifact schemas, recovery, agent adapters, and domain commands. Make these specifications sufficient to rebuild the controller without access to this skill or its current implementation.

Generate research.config.json with a schema version, research-contract version/hash, backend configuration by role, command argument arrays, stage input/output contracts, limits, and domain evaluator settings. Prefer JSON to avoid unnecessary YAML dependencies; allow YAML when the environment already supports it.

Generate a project-local `research` executable (or `research.ps1` on Windows), runtime/, prompts/, candidate/, experiments/, logs/, fixtures/ when needed, research.log.jsonl, RESULTS.md, and AGENTS.md. Create no global npm link. Resolve paths relative to the executable's project root, independent of invocation cwd. Separate immutable candidate revisions from the controller-managed current-candidate reference.

Define each role prompt with its exact inputs, permitted outputs, structured response schema, and forbidden controller-owned files. Make AGENTS.md explain the workflow and actual enforcement limitations. Specify domain commands such as benchmark, score, simulate, or evaluate only as the research requires.

## Generate the runtime

Implement `research describe`, `status`, `step`, `continue` (alias of step), `history`, `inspect <id>`, `validate`, and `doctor`. Make status and describe read-only. Make step perform exactly one stage attempt; verification rejection routes to a later build invocation. Never hide multiple agent roles or repair loops within one step.

Implement fresh backend sessions per role invocation, declared artifact dependencies, schema validation, controller-only state events, fixed evaluator execution, reproducible candidate snapshots, bounded retries, transactional candidate promotion, and resumable history updates. Follow the bundled contracts for concurrency and interrupted operations.

Keep experimental agents unable to change the evaluation contract, canonical history, event log, or current candidate within the chosen isolation mechanism. If the backend cannot enforce file restrictions, use a separate worker workspace and controller-mediated output import; report residual read/execution access honestly. Never describe prompts or cwd alone as a sandbox.

## Verify before handoff

Use a deterministic mock agent/evaluator and disposable fixtures to exercise the generated runtime without paid agent calls. Verify the normal lifecycle, verifier rejection and rebuild, malformed/missing artifacts, backend timeout/failure, crash recovery, duplicate step/concurrent lock contention, corrupted/torn log tail, failed promotion recovery, stale candidate parent, budget exhaustion, and execution from another cwd. Verify status does not mutate state and one step cannot invoke the next stage. Mock scores verify plumbing only, not scientific validity.

Inspect generated domain evaluation for correctness, leakage, fair controls, seeds, repeats, and metric meaning. Mark the harness unready if genuine fixtures or a baseline are unavailable. Do not claim a real backend works until its configured executable and permissions have been verified; use a bounded smoke invocation only when authorized and available.

For reconstruction, replay and validate existing records before changing runtime/. Preserve research IDs, schemas, artifact hashes, candidate lineage, and the event log. Implement explicit versioned migrations when required; never reinterpret old events under a changed contract silently.

Finish with the folder, chosen runtime/backend, readiness and verification status, and the exact local commands to inspect and advance it. Do not start an unattended loop unless asked.

# Headless agent adapters and role isolation

## Discover instead of guessing

Inspect each available executable's help/version and, when necessary, current official documentation. Verify noninteractive mode, prompt input, structured output, session creation, tool permission controls, cwd, timeout and exit behavior. Treat Codex, Cline, and GitHub Copilot as possible backends, not guaranteed commands. Do not hardcode speculative flags or assume similarly named tools share interfaces. Store executable, argument templates and capability evidence in environment/config records; do not store credentials.

Generate a small adapter interface:

```text
invoke(role, attemptId, inputManifest, outputDirectory, timeout, permissions)
 -> exitCode, stdoutLog, stderrLog, outputManifest, usageIfAvailable
```

Use new sessions for every invocation, including retries. Disable session resumption and implicit conversational memory where supported. Resolve prompt files via explicit arguments/stdin safely. Capture nonzero exits, signals, timeout, invalid JSON and missing outputs distinctly. Do not parse narrative stdout as a completion event.

## Role authority

| Role | Reads | May propose/write |
| --- | --- | --- |
| Planner | objective, candidate summary, relevant history | current hypothesis |
| Builder | hypothesis, evaluation contract, parent snapshot, prior audit | experiment plan and experimental workspace |
| Auditor | hypothesis, plan, workspace, fixed evaluation contract | verification output only |
| Analyst | hypothesis, plan, audit, measured results | analysis only |
| Selector | analysis, measurements, incumbent evidence, history | decision only |
| Historian | finalized experiment and history | history proposal only |

Auditors diagnose without repairing; route rejection back to a separate builder call. RUN belongs to the fixed controller evaluator, not an agent allowed to rewrite the benchmark. No worker appends events, edits controller config/runtime, overwrites canonical results, or promotes candidates.

## Enforce what is claimed

Tool allowlists restrict tool types; they may not restrict target paths. Read-only tools may still expose unintended files. Cwd is not isolation. A prompt is not access control. Record separately which permissions are backend-enforced, OS-enforced, or only advisory.

Where adequate path controls exist, configure them per role. Otherwise copy permitted inputs into a disposable worker workspace, run with an available OS/container boundary if applicable, and import only validated declared outputs. Without an OS boundary, disclose that same-user subprocesses may access the host despite controller-mediated import. Fail closed if the user's mandatory security restrictions cannot be enforced. Never automatically broaden permissions or use an allow-all flag to bypass a backend error.

Verifier outputs can be collected via structured stdout or a dedicated output directory even if source inputs are read-only. If shell access is needed for inspection, restrict it using supported controls and execution budgets. The domain candidate may also be executable untrusted code: apply a suitable runner boundary, timeout and input/output interface, and keep evaluator answers/controller state outside its allowed access.

Provide a deterministic mock adapter with fixture responses for lifecycle verification. Mock mode must identify itself in events/results, use a separate test research ID and never promote to a real project's incumbent. Do not leave mock mode silently active in a scientifically ready scaffold.

# Agent adapters, session policy and authority

## Capability discovery

Inspect actual executable help/version and current official docs where necessary. Verify noninteractive prompts, structured output, cwd, sessions, permissions, timeout and exit behavior. Codex, Cline and GitHub Copilot are possible backends, not assumed commands. Store executable plus argument arrays and verified capabilities, never credentials or speculative flags.

Use an adapter taking role/stage, attempt ID, input manifest, output directory, time/token limits, permissions and session policy. Return exit status, output manifest, separate stdout/stderr paths, session identity and actual/estimated/unknown usage. Distinguish timeout, signal, invalid output and process failure. Never parse narrative stdout as a state event.

## Sessions are a choice

| Policy | Benefit | Cost/risk | Appropriate use |
| --- | --- | --- | --- |
| Fresh per invocation | Explicit bounded context and reproducible input manifest | Repeated context/token cost; loses repair continuity | Independent audit, compact planning, unrelated experiments |
| Persistent builder within experiment | Efficient iterative repair and retained local understanding | Stale assumptions/context; larger session; contamination across revisions | Multiple implementation repairs with explicit refreshed contracts and audits |
| Deterministic controller, no model call | Cheap consistent measurement/decision/history rendering | Requires explicit rules | Evaluator execution, metric aggregation, adoption gates, factual summaries |

Default to fresh sessions for an independent auditor where one exists. Builders may reuse sessions within one experiment when the backend supports verified resumption. Never share builder context with an allegedly independent auditor or leak protected confirmation answers through prompts/history. Record session identity, reuse, provided artifacts, backend/model version and limits. Refresh inputs after repair and invalidate downstream evidence; reusing context does not reuse approval. Fresh sessions reduce shared conversational context but do not guarantee epistemic independence.

## Authority

Workers propose candidate/plan/rationale artifacts inside their declared outputs. Auditors, if configured, diagnose without repairing in that same invocation. Analysts interpret immutable observations. The fixed evaluator produces measurements; controller code aggregates and gates them. Only the controller appends events, commits promotion, or refreshes canonical history. Combined planning/building or analysis/recommendation is allowed in a declared stage; measurement authority remains separate.

Tool allowlists, path controls and OS isolation are distinct. Prompts and cwd are not a sandbox. Configure supported restrictions, or use a disposable workspace plus controller-mediated validated import. Without an OS boundary, acknowledge same-user processes may still access the host. Fail closed when mandatory restrictions cannot be enforced; do not broaden permissions automatically to get past an error. Apply an appropriate candidate execution boundary and time/resource limits; keep answer keys and controller state out of candidate access.

Mock adapters must identify mock provenance in all outputs, use a separate project namespace and never promote real incumbents. Mock measurements test control flow only. Verify a real backend with a bounded invocation when available and authorized; otherwise report integration unverified. Record failures and preserve attempts rather than silently switching provider/model and combining incomparable runs.

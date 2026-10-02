# Autoresearch Scaffold Skill — v2

Give an agent a research objective and a target folder. This skill teaches it to generate a local research controller using the runtimes and headless agent tools available in that environment. Durable design documents describe the research; a custom CLI advances one explicit stage per `research step`.

## Use

Install this folder using your agent's supported skill installation mechanism, or ask it to read `SKILL.md` and the linked references.

> Use autoresearch to set up research in ./fuzzy-match for the fastest approximate string matcher in JavaScript.

The scaffold selects a small default workflow or a fuller audited workflow, with a documented reason. It defines the correctness oracle and validates the evaluator before research, measures a baseline, records experiment evidence, and gates adoption through controller code. Inconclusive results can request another bounded measurement batch of the same frozen candidate. Session reuse and model costs are explicit choices.

## What changed in v2

Scientific readiness now includes independently justified oracle cases and deliberately defective candidates. Measurement guidance covers paired/interleaved benchmarks, warmup, independent observation units, noise pilots, uncertainty, repeated selection and protected confirmation. Budgets cover calls, time and available token/spend telemetry, with confirmation reserved before more exploration.

The role pipeline is configurable. JSON drives decisions; factual Markdown is rendered from it. Immutable artifacts are prepared before the journal completion record commits a change. Candidate pointers and summaries are derived views, so interrupted publication has one authority.

## Conformance

The skill includes a precise replay protocol, golden event logs, expected states, malformed examples, and a Python standard-library reference reducer/checker. See `references/protocol.md` for exact invocation and the fixture manifest. Generated runtimes must check their own replay implementation against the fixtures and separately test filesystem/process recovery.

Passing protocol fixtures does not validate an evaluator, prove OS isolation, or establish scientific improvement. Real domain controls and confirmation remain separate requirements. A reference reducer is not a universal research runtime.

See `references/agent-adapters.md` for backend capability discovery and session tradeoffs, `references/research-contract.md` for scientific and budget policies, and `references/foundations.md` for source attribution and limits.

## Reproducible validation

Run `python3 scripts/check_conformance.py` for the 25 replay vectors. Run `python3 examples/sum-of-squares/test_demo.py` for the bounded real evaluator and seven integration checks. See the example README for scope and limitations.

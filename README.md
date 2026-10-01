# Autoresearch

An agent skill that generates portable, domain-specific research environments.

Give an agent a research goal and target folder. The skill teaches it to build a local CLI using the runtimes and headless agent tools available in that environment. The resulting controller advances one stage per `research step`, validates artifacts, preserves experiment history, and recovers interrupted work.

## Usage

Install this folder as an agent skill using your agent's supported skill installation mechanism, or ask an agent to read `SKILL.md` and its referenced files.

Example request:

> Use autoresearch to set up research in ./fuzzy-match for the fastest approximate string matcher in JavaScript.

The generated project provides `research describe`, `status`, `step`, `continue`, `history`, `inspect`, `validate`, and `doctor`, plus domain-specific evaluation commands.

## Design

The lifecycle is hypothesis, build, verify, run, analyze, decide, and update. Each agent role uses a fresh session. The controller owns transitions, measurement records, and candidate promotion. Verification rejection returns to a later build step. JSONL events and versioned artifacts preserve state independently of implementation language.

The skill contains architectural contracts rather than a prebuilt universal runtime. Generated implementations require conformance tests and genuine scientific fixtures before research execution. Agent prompts and working directories are not security sandboxes.

See `references/` for runtime semantics, research schemas, backend adapters, and connections to Design Docs Are All You Need and Dream-RSI.

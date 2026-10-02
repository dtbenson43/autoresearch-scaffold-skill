# Bounded sum-of-squares demonstration

Run `python3 examples/sum-of-squares/test_demo.py` from the repository root on Linux or macOS. Tests create disposable research folders, perform real evaluation, inject interruptions, and remove those temporary folders afterward. Python standard library only; no network or paid model calls.

Run protocol compatibility with `python3 scripts/check_conformance.py --command python3 examples/sum-of-squares/research replay`.

This generated demonstrator uses deterministic imports of three checked-in candidate fixtures. The research agent backend is unavailable. It measures actual Python code and exhaustively checks its bounded mathematical domain; it does not demonstrate autonomous discovery or real agent integration. The runtime vendors the supplied reducer, so its fixture pass verifies integration with that implementation, not an independently implemented second-language reducer.

The oracle uses consecutive odd differences, independently of the multiplicative loop baseline and polynomial alternative. All 1001 supported inputs and six invalid inputs are checked. The intentionally incorrect candidate fails. Exploration and confirmation use separate evaluator invocations, each with six paired timing blocks. Results use a declared descriptive operational gate, not a statistical significance claim or general performance guarantee.

`validation-result.json` records one observed run. The decision may be inconclusive on another machine; the test accepts that. Recovery checks exercise process interruption, not physical power loss. Re-measurement is exercised only through a segregated synthetic replay fixture. The example is intentionally limited to trusted local candidate code and POSIX locking. Missing/malformed backend replies and all possible crash points are not exhaustively tested here.

For manual stepping in a disposable copy: `python3 research init`, then `python3 research step` until the explicit stopped exit. `python3 research status` is read-only. Configured evaluation reservations are charged before subprocess calls; no tokens or dollars are spent on agents. No unattended loop starts automatically.

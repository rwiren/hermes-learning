# Lesson: local-model-document-benchmark-stability

- Date: 2026-04-17
- Author: Hermie
- Related issue: #25
- Related branch: feature/local-model-doc-benchmark-stability-issue-25
- Related commits: <pending>

## Context
We needed a reproducible stability check for long document-improvement prompts in local Hermes model routing, then a clear default/override recommendation based on both latency and output-structure fidelity.

## What we did
1. Ran a 3x benchmark sweep for `qwen2.5:14b` and `qwen2.5-64k:latest` with the same long 14-section prompt shape.
2. Enforced output quality gates on each run:
   - required sections present (`Improved Document`, `Capability-to-Impact Matrix`, `Top 3 Risks and Mitigations`)
   - no tool/function-call JSON leakage in output
3. Calculated p50 and p95 latency from successful runs only.
4. Recorded run-level metadata (duration, stdout size, Hermes session_id) for traceability.

## Evidence
- Command outputs / logs:
  - Model `qwen2.5:14b`
    - Run 1: 71.81s, stdout_len=2034, sections_ok=true, session_id=`20260417_185706_9cd92c`
    - Run 2: 52.44s, stdout_len=1668, sections_ok=true, session_id=`20260417_185818_2eed1b`
    - Run 3: 55.13s, stdout_len=2066, sections_ok=true, session_id=`20260417_185910_fc3bf0`
    - Aggregate: successes=3/3, timeouts=0, p50=55.13s, p95=71.81s, min=52.44s, max=71.81s
  - Model `qwen2.5-64k:latest`
    - Run 1: 111.49s, stdout_len=4645, sections_ok=true, session_id=`20260417_190005_2ffb17`
    - Run 2: 74.82s, stdout_len=2779, sections_ok=true, session_id=`20260417_190157_7c6169`
    - Run 3: 69.34s, stdout_len=2276, sections_ok=true, session_id=`20260417_190312_e36f97`
    - Aggregate: successes=3/3, timeouts=0, p50=74.82s, p95=111.49s, min=69.34s, max=111.49s
- Metrics / artifacts:
  - Quality gate passed on all six runs (`all_sections_ok=true` for both models)
  - No tool JSON leakage on any run (`any_tool_json_leak=false` for both models)
- Files changed:
  - `learning/lessons/2026-04-17-local-model-doc-benchmark-stability.md`
  - `CHANGELOG.md`

## What we learned
- `qwen2.5:14b` is currently the best default for this workload on this machine: lower p50 and tighter upper bound.
- `qwen2.5-64k:latest` is slower in this benchmark but remains useful as an explicit override for heavier context windows.
- A 3-run p50/p95 sweep is enough to expose practical stability differences that single-run tests can hide.

## What to repeat
- Use identical prompt and timeout budgets across models.
- Require explicit section-header checks and JSON-leak checks in quality gate.
- Report run-level metadata plus p50/p95 for decision quality.
- Keep default on the fastest stable model; reserve long-context variant as an override.

## What to avoid
- Selecting model defaults from a single run.
- Comparing models with different prompt structures.
- Treating long-context model tags as universally better without latency validation.

## Skill candidate?
- [x] Yes (candidate: reproducible local Hermes doc-benchmark with p50/p95 and quality gates)

# Lesson: learning-vault-bootstrap-and-model-safety

- Date: 2026-04-17
- Author: Hermie
- Related issue: #20
- Related branch: feature/learning-vault-model-safety-issue-20
- Related commits: <pending>

## Context
We needed a durable in-repo structure for shared learning while safely tracking the `model/` folder in a public repository.

## What we did
1. Created `learning/` structure for lessons, skills, experiments, and templates.
2. Added templates and operating rules for consistent documentation.
3. Added strict allowlist guardrails for `model/` to prevent accidental artifact leakage.

## Evidence
- Branch: `feature/learning-vault-model-safety-issue-20`
- Files added/updated in this change set.

## What we learned
A small, strict repository policy plus templates is enough to enforce sustainable learning capture and safe public model metadata tracking.

## What to repeat
- Introduce guardrails first (`.gitignore` + local directory policy)
- Then add documentation templates and a bootstrap lesson
- Validate for secrets and large files before every push

## What to avoid
- Tracking model binaries in git
- Mixing generated outputs with source-of-truth learning notes

## Skill candidate?
- [x] Yes (candidate: "learning-vault bootstrap + model safety checks")

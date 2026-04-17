# Learning Vault

This folder captures our shared learning in `hermes-learning` so insights do not disappear between sessions.

## Purpose
- Preserve what we learned (technical + process)
- Explain how we learned it (experiments, evidence, pitfalls)
- Convert repeated workflows into reusable skills/playbooks

## Structure
- `learning/lessons/` — dated lessons learned
- `learning/skills/` — candidate skill specs before promotion
- `learning/experiments/` — experiment notes and outcomes
- `learning/templates/` — reusable templates for consistent documentation

## Operating Rules
1. Every meaningful discovery should produce one concise note.
2. Each note must include evidence (logs, metrics, commit refs, issue links).
3. Separate facts from assumptions.
4. Mark reusable patterns for future skill creation.
5. Never store secrets, tokens, private keys, or sensitive personal data.

## Minimal workflow
1. Create a lesson note from template.
2. Link issue/branch/commit proving the change.
3. Add "What to repeat" and "What to avoid".
4. If pattern repeats, promote to a formal skill.

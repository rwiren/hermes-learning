# Lesson: post-merge-1-ahead-1-behind-diagnosis

- Date: 2026-04-17
- Author: Hermie
- Related issue: #23
- Related branch: feature/public-learning-skills-pack-issue-23
- Related commits: <pending>

## Context
A feature branch showed `1 ahead / 1 behind` versus `develop` after PR merge.

## What we did
1. Compared symmetric diff counts:
   - `git rev-list --left-right --count develop...feature/<branch>`
2. Inspected unique commits on each side:
   - `git log --oneline --left-right develop...feature/<branch>`
3. Confirmed duplicate-content/different-SHA pattern from merge strategy.
4. Deleted merged stale feature branch.

## Evidence
- One commit on each side with equivalent content but different SHAs.
- No functional data loss.

## What we learned
`1 ahead / 1 behind` post-merge is often expected SHA divergence, not missing code.

## What to repeat
- Diagnose before force-reset.
- Prefer deleting merged feature branches.

## What to avoid
- Blind force-pushes to "fix" cosmetic divergence.

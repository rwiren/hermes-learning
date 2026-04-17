# Lesson: gui-conflict-resolution-local-sync

- Date: 2026-04-17
- Author: Hermie
- Related issue: #23
- Related branch: feature/public-learning-skills-pack-issue-23
- Related commits: <pending>

## Context
Manual conflict resolution was completed in Git GUI and local repository needed deterministic sync verification.

## What we did
1. Verified repo root, remotes, current branch, and status.
2. Fetched/pruned all remotes.
3. Fast-forwarded `develop` and `main` to origin.
4. Verified ahead/behind matrix for all local branches.
5. Removed stale local feature branches after merge cleanup.

## Evidence
- `develop` and `main` both at `0 ahead / 0 behind` vs origin.
- Working tree clean on `develop`.

## What we learned
GUI conflict resolution is fine, but terminal reconciliation is still required to prove branch parity and cleanup stale refs.

## What to repeat
- Always run post-GUI sync checklist.
- Always confirm branch parity with `rev-list --left-right --count`.

## What to avoid
- Assuming GUI merge implies all local branches are clean.
- Leaving stale local feature branches after merge.

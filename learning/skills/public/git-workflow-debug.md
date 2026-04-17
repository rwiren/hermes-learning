# Public Skill: Git Workflow Debugging

## Purpose
Recover quickly from branch drift, wrong-branch commits, and post-merge divergence.

## Baseline checks
```bash
git rev-parse --show-toplevel
git remote -v
git status
git fetch --all --prune --tags
git branch -vv
```

## Scenario A: branch behind remote
```bash
git checkout develop
git pull --rebase origin develop
```

## Scenario B: commit landed on wrong branch
```bash
git checkout <wrong_branch>
git reset --soft HEAD~1
git checkout -b feature/<topic>
git commit -m "feat: <message>"
```

## Scenario C: post-merge "1 ahead / 1 behind"
Verify:
```bash
git rev-list --left-right --count develop...feature/<branch>
git log --oneline --left-right develop...feature/<branch>
```
If duplicate-content/different-SHA, cleanup:
```bash
git checkout develop
git branch -d feature/<branch>
```

## Policy
- Never push directly to `main`.
- Use issue-driven `feature/*` branches from `develop`.
- Use Conventional Commits.

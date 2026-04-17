# Lesson: launchctl-bootstrap-error-5-race-recovery

- Date: 2026-04-17
- Author: Hermie
- Related issue: #23
- Related branch: feature/public-learning-skills-pack-issue-23
- Related commits: <pending>

## Context
`hermes gateway install --force` failed on macOS with launchctl bootstrap exit status 5 (`Input/output error`).

## What we did
1. Validated plist syntax and service state.
2. Inspected launchd diagnostics.
3. Observed internal launchd message: `Operation already in progress`.
4. Applied controlled recovery sequence:
   - bootout -> short wait -> bootstrap -> kickstart
5. Patched local gateway launcher to use bootout + retry/backoff bootstrap strategy.

## Evidence
- Service successfully reloaded and reported running after recovery.
- Repeated force installs no longer failed in validation run.

## What we learned
launchd bootstrap failures can be transient orchestration races; robust retry/backoff logic makes install flow reliable.

## What to repeat
- Confirm root cause in launchd logs before changing code.
- Serialize restart/install operations.

## What to avoid
- Running concurrent gateway reinstall/restart commands.
- Treating exit code 5 as always a permanent plist problem.

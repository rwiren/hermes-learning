# Public Skill: macOS launchd bootstrap race recovery

## Symptom
`launchctl bootstrap ...` fails with:
- `Input/output error` (exit 5)
- internal `Operation already in progress`

## Root cause
launchd teardown/bootstrap race when service label is being replaced quickly.

## Recovery sequence
```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway || true
sleep 5
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
```

## Stable operating pattern
- Avoid parallel `gateway restart/install` calls from multiple shells.
- Prefer stop -> wait -> start when service is unstable.

## Validation
```bash
hermes gateway status
launchctl print gui/$(id -u)/ai.hermes.gateway
```

# Public Skill: Signal CLI Operations (Sanitized)

## Purpose
Send Signal messages safely from terminal workflows while avoiding common daemon lock conflicts.

## When to use
- Operational notifications from scripts
- Group updates from CI/automation
- Controlled outbound messaging from a local agent

## Preconditions
- `signal-cli` installed
- Account registered
- Signal daemon endpoint configured

## Safe command pattern
```bash
# Stop stale lock holders (if any)
pkill -9 -f signal-cli 2>/dev/null || true
sleep 2

# Send message (placeholder identifiers only)
signal-cli -a <PHONE_NUMBER> send -g <SIGNAL_GROUP_ID> -m "<MESSAGE>"

# Restart daemon
nohup signal-cli -a <PHONE_NUMBER> daemon --http 127.0.0.1:8080 >/dev/null 2>&1 &
sleep 2

# Restart gateway process so it reconnects cleanly
hermes gateway restart
```

## Common failure
`Config file is in use by another instance, waiting…`

### Fix
1. Stop stale signal-cli processes.
2. Re-run send command.
3. Restart daemon.
4. Restart gateway.

## Security notes
- Never publish real phone numbers or group IDs.
- Use placeholders only: `<PHONE_NUMBER>`, `<SIGNAL_GROUP_ID>`.
- Do not include `.env` values in docs.

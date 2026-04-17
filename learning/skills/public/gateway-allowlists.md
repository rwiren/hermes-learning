# Public Skill: Gateway Allowlists (Signal + Discord)

## Purpose
Configure who can interact with gateway platforms using environment-based allowlists.

## Core principle
Access control lives in `~/.hermes/.env`, not `config.yaml`.

## Discord
- `DISCORD_ALLOWED_USERS` = comma-separated user IDs/usernames
- `DISCORD_ALLOWED_CHANNELS` = comma-separated numeric channel IDs only

## Signal
- `SIGNAL_ALLOWED_USERS` = comma-separated phone numbers (for DMs)
- `SIGNAL_GROUP_ALLOWED_USERS` = comma-separated group IDs

## Apply changes
```bash
hermes gateway restart
```

## Verification
- Check gateway logs for unauthorized access events
- Confirm allowed users/channels can message successfully

## Security
- Never commit real IDs/numbers to git.
- Use placeholders:
  - `<DISCORD_USER_ID>`
  - `<DISCORD_CHANNEL_ID>`
  - `<PHONE_NUMBER>`
  - `<SIGNAL_GROUP_ID>`

# model/ directory policy

This directory stores model configuration metadata for reproducible local experiments.

Tracked files in this public repository:
- `Modelfile` (recipe/instructions)
- `README.md` (this policy)
- `.gitignore` (allowlist guard)

Not allowed in git:
- model binaries (`*.gguf`, `*.bin`, `*.safetensors`, checkpoints)
- private or licensed weight files
- tokens, credentials, or local environment exports

Workflow:
1. Keep heavy model files local/outside this repo.
2. Keep only reproducible metadata and references here.
3. Run a sensitivity and file-size sanity check before each push.

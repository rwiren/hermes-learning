# Public Skill: Learning Vault Bootstrap + Model Safety

## Purpose
Create a reusable in-repo learning workspace and enforce safe public model metadata tracking.

## Steps
1. Create issue + milestone.
2. Branch from updated `develop`.
3. Add `learning/` structure:
   - `lessons/`
   - `experiments/`
   - `skills/`
   - `templates/`
4. Add model safety allowlist rules:
   - track only `model/Modelfile`, `model/README.md`, `model/.gitignore`
5. Update README + CHANGELOG.
6. Run sensitivity and large-file scans before push.

## Mandatory checks
- Secret-pattern scan on changed files
- Large-file scan threshold check
- Ensure no real credentials/IDs in docs

## Output
A maintainable knowledge base that is safe for public git.

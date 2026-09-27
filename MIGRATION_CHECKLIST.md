# Migration Checklist

## Phase 1 — Freeze knowledge before cleanup

- [ ] Copy this handoff package into the repository.
- [ ] Read every document and correct any path/name that differs from the real repository.
- [ ] Replace both prompt placeholders with exact prompt text from the original scripts.
- [ ] Verify canonical artifact paths.
- [ ] Compute SHA-256 hashes from the real repository artifacts.
- [ ] Record current git commit, if one exists.
- [ ] Verify `.gitignore` before adding files.
- [ ] Search repository for API keys/tokens/secrets.
- [ ] Create a baseline commit.
- [ ] Tag baseline, e.g. `research-baseline-v1`.

## Phase 2 — Read-only OpenCode audit

Use the prompt in `OPENCODE_READ_ONLY_AUDIT.md`.

Do not allow file modifications during this phase.

- [ ] Reconstruct actual pipeline.
- [ ] Map scripts to pipeline stages.
- [ ] Identify canonical inputs/outputs.
- [ ] Identify duplicate/obsolete-looking artifacts.
- [ ] Identify methodological discrepancies.
- [ ] Identify secrets and machine-specific files.
- [ ] Produce proposed cleanup plan.
- [ ] Review plan manually.

## Phase 3 — Controlled cleanup

- [ ] Create cleanup branch.
- [ ] Apply only low-risk moves/deletions first.
- [ ] Preserve all files marked for manual review.
- [ ] Update paths.
- [ ] Run validations.
- [ ] Compare canonical counts/hashes where applicable.
- [ ] Confirm no methodological parameter changed.
- [ ] Review `git diff`.
- [ ] Commit cleanup separately from scientific changes.

## Phase 4 — Annotation protocol

- [ ] Preserve pair-level human annotation as gold-standard authority.
- [ ] Keep preliminary security relevance separate.
- [ ] Decide author-validation sampling protocol for security relevance.
- [ ] Avoid exposing preliminary security labels during independent author validation if measuring agreement.
- [ ] Record final protocol in `docs/decisions.md`.

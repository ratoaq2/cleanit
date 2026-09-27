---
name: release
description: Release a new version to PyPI through a GitHub release, with clean release notes.
disable-model-invocation: true
---

# Release

A GitHub release starts two workflows: `publish.yml` publishes to PyPI, and `docker-publish.yml` publishes
the Docker image. You cannot undo a publish.

## Steps

1. Be on an up-to-date `main` with a clean tree. `bash scripts/test.sh` must pass.
2. Find the version in `pyproject.toml` and the last tag (`git describe --tags --abbrev=0`). Propose the
   new version from the changes since the last tag. The tag has no `v` prefix (`0.2.0`), unless the
   existing tags have one.
3. Update the version: remove the `-dev` suffix in `pyproject.toml`. In `HISTORY.md`, change
   `## Unreleased` to `## <version>`, and add a `**Release date:** <yyyy-mm-dd>` line below it. Add a new
   empty `## Unreleased` section above it. Commit with `chore: release <version>` through a PR.
4. Generate the notes:

   ```bash
   gh api repos/{owner}/{repo}/releases/generate-notes -f tag_name=<tag> -f target_commitish=main --jq .body > notes.md
   ```

5. Edit `notes.md`:
   - Remove the "What's Changed" lines for PRs from `dependabot[bot]` or from `dependabot/` branches.
   - Remove the "New Contributors" lines for `dependabot[bot]` and for the repository owner.
   - Remove each section that is then empty, with its heading.
6. **Show the tag, the target branch, and the notes to the user. Wait for approval.**
7. Run `gh release create <tag> --target main --title <tag> --notes-file notes.md`.
8. Check the runs: `gh run list --workflow publish.yml --limit 1` and
   `gh run list --workflow docker-publish.yml --limit 1`.
9. After the publish, set the next development version in `pyproject.toml`, for example `0.5.3-dev`
   (`chore: back to development`).

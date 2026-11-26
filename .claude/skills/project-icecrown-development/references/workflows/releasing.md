# Releasing

Publishing is an ask-first item: nothing is published without the owner's explicit confirmation.
The pipeline is `.github/workflows/release.yml` ([qa-and-ci.md](../qa-and-ci.md#ci-workflows)).

1. **Ask first**: the version, the changelog entry, and go / no-go.
2. In a pull request: set the version in `pyproject.toml` (its only home), move the "Unreleased"
   changelog entries under the new version with today's date, and update the roadmap's status row.
3. After the merge, the owner tags the merge commit: `git tag -s vX.Y.Z` and pushes the tag.
4. The workflow builds the sdist and wheel once, checks that the tag matches the package version,
   and attests the build.
5. The job pauses at the approval gate of its environment (`testpypi` for a `.devN` rehearsal, then
   `pypi`); the owner approves.
6. Trusted publishing uploads the files with their attestations; the GitHub Release is created from
   the changelog entry.
7. Check the release page and install the published version in a clean environment.

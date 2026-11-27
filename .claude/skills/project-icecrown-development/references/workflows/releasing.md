# Releasing

Publishing is an ask-first item: nothing is published without the owner's explicit confirmation.
The pipeline is `.github/workflows/release.yml` ([qa-and-ci.md](../qa-and-ci.md#ci-workflows)).

1. **Ask first**: the version, the changelog entry, and go / no-go.
2. In a pull request: set the version in `pyproject.toml` (its only home), move the "Unreleased"
   changelog entries under the new version with today's date, and update the roadmap's status row.
   A `.devN` rehearsal needs no entry of its own; its notes are the "Unreleased" section.
3. After the merge, the owner tags the merge commit (`git tag vX.Y.Z`, signed with `-s` where a
   signing key is set up) and pushes the tag. Only repository admins can create `v*` tags.
4. The `build` job refuses a tag whose commit is not on `main`, checks the tag against the version
   and the changelog (`tools/release_notes.py`), builds the sdist and the wheel once and checks their
   metadata; it holds no OIDC token. The `attest` job then attests the files (SLSA build
   provenance).
5. `publish to TestPyPI` waits at the `testpypi` environment's approval gate; the owner approves;
   trusted publishing uploads the files with their PEP 740 attestations.
6. The owner checks the TestPyPI page and a test install (`pip install -i
   https://test.pypi.org/simple/ icecrown==X.Y.Z`), then approves `publish to PyPI` at the `pypi`
   gate.
7. The GitHub Release is created from the changelog entry, marked as a pre-release for `aN`, `bN`,
   `rcN` and `.devN` versions, with the distributions attached.
8. Check the release page and install the published version in a clean environment.

## When a release run fails

`ci-build` runs the tag check (`tools/release_notes.py`) on every pull request, so a version
without its changelog entry fails before it is tagged. If a run still fails after the tag, the tag
stays — `v*` tags can be neither moved nor deleted. Fix the cause in a pull request and release the
next version (`X.Y.Z+1`, or `.devN+1` for a rehearsal); the failed tag gets no release. A failure
after TestPyPI succeeded can be re-run from the `pypi` job once its cause is fixed outside the
code.

## One-time setup (owner)

- On PyPI and TestPyPI, add a pending trusted publisher for project `icecrown`: repository
  `Deluha/icecrown`, workflow `release.yml`, environment `pypi` (PyPI) or `testpypi` (TestPyPI).
  A pending publisher does not reserve the name; the first upload does.
- In the repository settings, create the environments `testpypi` and `pypi` with the owner as
  required reviewer and deployments limited to `v*` tags.

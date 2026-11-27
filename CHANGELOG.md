# Changelog

All notable changes to Project Icecrown are recorded here, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/); what is covered is in the
[compatibility promise](docs/compatibility.md).

## [Unreleased]

### Added

- Phase 0, Light's Hammer: packaging (`src/` layout, `py.typed`, `pyarrow>=18.0.0` as the only
  runtime dependency, `pandas` and `sql` extras), the quality gates (ruff, mypy strict, pytest with
  offline tests, Hypothesis, 90 % branch coverage, pre-commit, gitleaks), the development guidance and
  its checkers, the one verify command, CI on Python 3.11–3.15 across Linux, macOS and Windows, supply
  chain hardening, the release pipeline with trusted publishing and attestations, and the
  documentation site with the compatibility promise.

[Unreleased]: https://github.com/Deluha/icecrown/commits/main

# Compatibility promise

What a user of Project Icecrown can rely on from one release to the next, and how a change to it is
announced.

## What is public

- The names listed in `icecrown.__all__`, with their documented signatures and behaviour.
- The exception hierarchy: `IcecrownError` and its documented subclasses.
- The `icecrown` command: its commands, flags and exit codes.
- The pytest plugin: the `frostmourne` fixture and the plugin's command-line options.
- The `icecrown.toml` configuration schema.
- The store format: the `.icecrown/` layout and the baseline-file format
  ([reference](reference/store-format.md)).
- The fingerprint specification ([reference](reference/fingerprint-spec.md)).
- The JSON report schema.

Everything else is private and may change in any release: every module or name that starts with an
underscore, the wording and layout of console output and Markdown reports, and the banner.

## Version numbers

Project Icecrown follows [Semantic Versioning](https://semver.org/). The version lives only in the
package metadata.

- **Before 1.0** (`0.y.z`): a minor release (`0.y`) may change or remove a public item; each such
  change is listed in the changelog under *Changed* or *Removed*, with what to do instead. A patch
  release (`0.y.z`) never breaks a public item.
- **From 1.0**: a public item changes incompatibly only in a major release.

## Deprecation

A public item is deprecated before it is removed whenever that is possible: it keeps working, emits
a `DeprecationWarning` (in Python) or a warning on standard error (in the command), and is listed in
the changelog under *Deprecated* with its replacement. It is removed no earlier than the next minor
release before 1.0, and the next major release from 1.0.

## The two format versions

The store format and the fingerprint specification are versioned separately from the package and
from each other; both versions are written into every baseline file.

- From the 0.1.0 release on, every release reads every earlier store-format version — migrating it —
  or refuses it with a clear error that names the command to run.
- A fingerprint-specification change never silently changes the result of `verify`: a baseline
  written under an earlier specification is verified under that specification, or refused with a
  clear "freeze again" error.
- Within one specification version, the same data and capture options give the same fingerprint on
  every operating system, CPU architecture, Python version and dependency version the release
  supports.

## Supported versions

- **Python**: every CPython version that is not end-of-life, from 3.11. Support for a version that
  reaches its end of life is dropped in a minor release and announced in the changelog.
- **Dependencies**: each has a stated lower bound, tested in CI together with the latest release.
  Raising a lower bound is announced in the changelog.
- **Fixes**: only the latest release receives fixes, security fixes included.

## What the fingerprint does not promise

The fingerprint detects accidental change. It is not a defence against a party who deliberately
constructs a colliding dataset, and since its hashes are unsalted, a baseline of small or
low-entropy data does not keep that data secret.

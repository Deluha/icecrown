# Changing the store format

The store format is the `.icecrown/` layout and the baseline-file JSON. It is an ask-first item, and
it is versioned separately from the fingerprint spec.

1. **Ask first**, in the [decision format](../recipes.md#decision-format), with a sample of the
   file before and after.
2. Update the reference in `docs/reference/store-format.md` first.
3. Bump the store-format version in `_versions.py` (R1, R6).
4. Keep the baseline file stable: sorted keys, LF line endings, no timestamp, no user or machine
   name, no cell value, no row hash.
5. From the 0.1.0 tag on: ship a migration that reads the previous version, or a clear error that
   names the command to run; add a compatibility test with a committed sample of the old format.
6. Changelog entry under *Changed*, naming the store-format version (R7).
7. Run [the verify command](../qa-and-ci.md#verify), then the `reviewer`.

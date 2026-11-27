# Changing the fingerprint

Anything that changes the bytes hashed for a dataset — canonicalisation, the hash, the row encoding,
the combination, a logical type — changes the fingerprint spec. It is an ask-first item.

1. **Ask first**, in the [decision format](../recipes.md#decision-format): what changes, why, and
   which existing baselines stop matching.
2. Update the spec in `docs/reference/fingerprint-spec.md` *before* the code, with new test vectors.
3. Bump the fingerprint-spec version in `_versions.py` (R1, R6).
4. Change the code in the [fingerprint path](../architecture.md#module-map) only; keep it
   deterministic (R3, checker C2).
5. Update the test vectors and the golden fingerprints; never edit a golden value without the spec
   change that explains it.
6. From the 0.1.0 tag on: a baseline written under the old spec gives a clear "freeze again" error,
   or is still verified under the old spec; add a compatibility test either way.
7. Changelog entry under *Changed*, naming the spec version (R7).
8. Run [the verify command](../qa-and-ci.md#verify), then the `reviewer`.

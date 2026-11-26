# Adding a source

A source turns a reference into Arrow record batches with logical types (Gunship Battle). The
adapter contract is fixed in Phase 2 and documented under `docs/`.

1. **Ask first** if the source needs a new runtime dependency; an optional extra is the default.
2. Read the source registry and one existing adapter in `src/icecrown/_sources/`
   ([architecture.md](../architecture.md#module-map)).
3. Add one module, `_sources/<name>.py`, and register it in the registry (R1); never branch on a
   source name elsewhere.
4. Import an optional dependency lazily; a missing extra raises an error naming the extra
   ([conventions.md](../conventions.md#module-layout)).
5. Map every native type to a logical type, or refuse it with a clear error. The fingerprint must not
   depend on the source: add a test that the same logical data through this source and through Arrow
   gives the same fingerprint.
6. Tests are offline (R5): files under `tmp_path`, in-memory databases, synthetic result sets.
7. Document the source and its options under `docs/` and add a changelog entry (R7).
8. Run [the verify command](../qa-and-ci.md#verify), then the `reviewer`.

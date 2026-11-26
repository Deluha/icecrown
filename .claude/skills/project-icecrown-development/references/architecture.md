# Architecture

Where things live and how data moves. The codename list and the phase plan are in
[ROADMAP.md](../../../../ROADMAP.md#codenames); this file maps them onto modules.

## Module map

All modules are private (`_*.py`) except the public package `__init__.py` and the declared entry
points. Planned modules carry the phase that adds them.

| Module | Codename | Holds | Phase |
|---|---|---|---|
| `icecrown/__init__.py` | — | The public API: re-exports and `__all__` | 0 |
| `_versions.py` | Frozen Throne | The format-version registry: store-format and fingerprint-spec versions | 1 |
| `_errors.py` | — | The exception hierarchy, rooted at `IcecrownError` | 1 |
| `_messages.py` | — | Console message helpers and the banner | 1 |
| `_types.py` | Frostmourne | The logical-type registry on Arrow | 1 |
| `_canon.py` | Frostmourne | Canonical byte form of each cell | 1 |
| `_fingerprint.py` | Frostmourne | Row hashes, content and schema fingerprints | 1 |
| `_soul.py` | Frostmourne | The `Soul` baseline object and its stable JSON form | 1 |
| `_store.py` | Frozen Throne | `.icecrown/` layout, snapshot names, atomic writes | 1 |
| `_frozen.py` | Frozen Throne | Optional frozen copies (Parquet) | 1 |
| `_sources/` | Gunship Battle | The source registry and one module per adapter | 2 |
| `_config.py` | Gunship Battle | `icecrown.toml` | 2 |
| `__main__.py` | Gunship Battle | The `icecrown` command (entry point, flow only) | 2 |
| `_findings.py` | Lord Marrowgar | The finding model and its console rendering | 3 |
| `_schema_diff.py` | Lord Marrowgar | Schema comparison of two souls | 3 |
| `_row_diff.py` | Blood Prince Council | Keyed reconciliation and value diff | 4 |
| `_gate.py` | Deathbringer Saurfang | `verify` / `accept` decisions with tolerances | 5 |
| `pytest_plugin.py` | Deathbringer Saurfang | The `frostmourne` fixture (entry point, flow only) | 5 |
| `_reports/` | Lady Deathwhisper | Markdown and JSON reports | 6 |
| `_suite.py` | The Lich King | Running every declared snapshot as one | 7 |

The fingerprint path — the modules checker C2 guards — is `_types.py`, `_canon.py`,
`_fingerprint.py` and `_soul.py`.

## Data flow

1. **Read.** A source adapter turns a reference (a file, a table, a query) into Arrow record batches.
2. **Type.** Each column maps to a logical type; storage width and dictionary encoding drop away.
3. **Canonicalise.** Each cell becomes a canonical byte form with a type tag and a length prefix.
4. **Hash.** Cells bind to their column names in sorted-name order and hash into row hashes; row
   hashes combine into the content fingerprint, beside the schema fingerprint and per-column
   fingerprints.
5. **Store.** `freeze` writes the soul to `.icecrown/snapshots/<name>.json` and, on request, a frozen
   copy to `.icecrown/frozen/`.
6. **Verify.** `verify` recomputes the soul with the recorded options and compares; on a mismatch,
   the diffs explain it (schema from the souls; rows and values from a frozen copy or a second
   source).

## Format versions

Two independent versions live in `_versions.py` and are written into every baseline file: the
store-format version and the fingerprint-spec version. Their published references are
`docs/reference/store-format.md` and `docs/reference/fingerprint-spec.md`.

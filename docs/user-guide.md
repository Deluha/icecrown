# User guide

```{note}
This guide grows with each phase of the roadmap. It will cover installation, freezing a dataset,
verifying it in CI, reading a diff, and accepting an intended change.
```

## Installation

```bash
pip install icecrown
```

The only runtime dependency is `pyarrow`. The pandas adapter and the SQL source are optional extras:
`pip install "icecrown[pandas]"` and `pip install "icecrown[sql]"`.

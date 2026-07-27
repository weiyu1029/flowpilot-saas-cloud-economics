# Data

- `raw/` contains deterministic synthetic source-like tables in CSV and Parquet.
- `curated/` contains analytics-ready customer, feature, service, executive, anomaly, recommendation, and quality models.
- `processed/` is reserved for intermediate outputs.

Regenerate everything with:

```bash
python scripts/run_pipeline.py
```

The generator uses seed `20260721`; outputs should be reproducible given the pinned environment. Rates are illustrative and not AWS billing estimates.

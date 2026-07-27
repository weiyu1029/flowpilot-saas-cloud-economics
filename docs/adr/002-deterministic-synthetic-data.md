# ADR 002 — Publish Deterministic Synthetic Data

**Status:** Accepted

## Decision
Generate all public portfolio data with a fixed seed and check curated files into the repository.

## Rationale
This avoids PII, keeps the app reproducible, permits controlled business scenarios, and makes deployment independent of private cloud credentials.

## Trade-offs
Synthetic behavior cannot establish production validity and requires transparent limitations.

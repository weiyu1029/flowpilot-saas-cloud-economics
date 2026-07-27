# ADR 001 — Use a Serverless-First Analytics Architecture

**Status:** Accepted

## Decision
Use S3, Lambda/Glue, Athena, CloudWatch, SNS, and Budgets as the reference AWS architecture.

## Rationale
The workload is intermittent, analytical, portfolio-scale, and cost-sensitive. Serverless services reduce always-on management while preserving measurable cost units.

## Trade-offs
Athena performance depends on file format/partitioning; serverless limits and cold starts exist; BI concurrency may eventually justify Redshift or another warehouse.

# Security, Reliability, and Cost Considerations

## Security
- Use root only for root-only tasks and enable MFA.
- Prefer IAM roles and short-lived credentials; never commit access keys.
- Apply least privilege to S3, Glue, Athena, Lambda, CloudWatch, and SNS.
- Enable S3 Block Public Access and encryption at rest.
- Use HTTPS/TLS for data in transit.
- Store application secrets in Streamlit Secrets, Secrets Manager, or Parameter Store—not source control.
- Use CloudTrail for API audit history and AWS Config for resource-configuration compliance.
- Treat synthetic data as public-safe; production customer data requires classification, retention, residency, and access review.

## Reliability and observability
- Log pipeline start/end, row counts, validation failures, and output keys.
- Alarm on ETL failures, stale data, unusual log ingestion, budget thresholds, and anomalous service cost.
- Use dead-letter queues and idempotent processing in a production event-driven design.
- Record data freshness in the UI and provide a runbook for failed refreshes.

## Cost controls
- Start with AWS Budgets and Cost Explorer.
- Tag resources with `project`, `environment`, `owner`, and `expiration`.
- Convert CSV to Parquet and partition by month to reduce Athena scanned bytes.
- Use Athena workgroups with enforced output and query limits.
- Avoid persistent NAT Gateway, RDS, OpenSearch, Redshift, or SageMaker endpoints for a small portfolio unless their business need is demonstrated.
- Stop or terminate EC2 labs; deregister unused AMIs and delete associated snapshots.
- Use Savings Plans only after demand is stable; do not buy commitments merely because a discount exists.

## Threat model highlights
| Threat | Control |
|---|---|
| Public data exposure | S3 Block Public Access, bucket policies, encryption |
| Credential leakage | IAM roles, secret stores, `.gitignore`, scanning |
| Excessive permissions | Least-privilege policy and access review |
| Unbounded query cost | Athena workgroup bytes-scanned cutoff |
| Silent pipeline failure | CloudWatch alarms and SNS notifications |
| Misleading recommendations | Explainable formulas, confidence, human review |

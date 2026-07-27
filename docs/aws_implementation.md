# AWS Implementation Guide

> The local and Streamlit Community Cloud version requires no AWS account. The infrastructure files are a reference implementation. Review every resource and cost before deploying.

## Suggested sequence
1. Create $1, $5, and forecast budget alerts.
2. Deploy or manually create an encrypted S3 bucket with public access blocked.
3. Upload curated Parquet data under dataset-specific prefixes.
4. Create the Glue database and Athena external tables.
5. Use the dedicated Athena workgroup for all portfolio queries.
6. Add Lambda/Glue only when demonstrating automated ingestion.
7. Configure CloudWatch alarms and SNS notifications.
8. Validate IAM least privilege and clean up all resources after the lab.

## Reference files
- `infra/cloudformation.yaml` — S3, Glue database, Athena workgroup, SNS, and AWS Budget.
- `infra/lambda/handler.py` — CSV-to-Parquet event transformation example.
- `infra/athena/create_tables.sql` — external-table DDL.
- `infra/athena/views.sql` — reusable analytics views.
- `infra/iam/least_privilege_policy.json` — replace placeholders before use.

## Important caveats
- CloudFormation creates chargeable resources and may consume credits.
- Confirm the email subscription sent by SNS.
- Replace placeholder bucket names and email addresses.
- Use IAM roles, not long-lived access keys.
- Delete stacks, query result buckets, snapshots, and retained resources after practice.

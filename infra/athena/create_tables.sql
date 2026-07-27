-- Replace ${DATA_BUCKET} with your S3 bucket name.
CREATE EXTERNAL TABLE IF NOT EXISTS flowpilot_cloud_economics.customer_monthly (
  month date,
  customer_id string,
  plan_type string,
  seat_count int,
  mrr_usd double,
  company_name string,
  industry string,
  company_size_segment string,
  region string,
  active_users int,
  feature_adoption_rate double,
  allocated_cloud_cost_usd double,
  cost_to_revenue_ratio double,
  estimated_gross_margin_pct double,
  margin_risk_tier string,
  customer_health_score double,
  revenue_at_risk_usd double
)
STORED AS PARQUET
LOCATION 's3://${DATA_BUCKET}/curated/customer_monthly/';

CREATE EXTERNAL TABLE IF NOT EXISTS flowpilot_cloud_economics.feature_monthly (
  month date,
  feature_name string,
  eligible_customers int,
  active_users int,
  adopted_customers int,
  feature_adoption_rate double,
  feature_cloud_cost_usd double,
  cost_per_active_user_usd double,
  cost_share_pct double,
  mom_cost_growth_pct double,
  economics_quadrant string
)
STORED AS PARQUET
LOCATION 's3://${DATA_BUCKET}/curated/feature_monthly/';

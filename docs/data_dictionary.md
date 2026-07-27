# Data Dictionary

All datasets are deterministic synthetic data generated with seed `20260721`. Parquet mirrors are included for analytics efficiency.

## Raw datasets

### `budgets_monthly.csv`
- Row count: **18**
- Columns: `month`, `budget_usd`, `actual_cost_usd`, `forecast_cost_usd`, `variance_usd`, `variance_pct`

### `cloud_cost_allocations_monthly.csv`
- Row count: **121,538**
- Columns: `month`, `customer_id`, `feature_name`, `aws_service`, `environment`, `usage_quantity`, `usage_unit`, `cost_usd`, `allocation_method`, `plan_type`, `mrr_usd`

### `customers.csv`
- Row count: **480**
- Columns: `customer_id`, `company_name`, `industry`, `company_size_segment`, `region`, `country`, `signup_date`, `churn_date`, `initial_plan`, `contract_type`, `account_owner`, `risk_profile`, `power_user_flag`, `underpriced_flag`, `planned_upgrade_month`

### `feature_metadata.csv`
- Row count: **9**
- Columns: `feature_name`, `product_area`, `release_date`, `minimum_plan`, `primary_aws_service`, `primary_usage_metric`, `business_value`

### `incidents.csv`
- Row count: **113**
- Columns: `incident_id`, `incident_date`, `month`, `aws_service`, `feature_name`, `severity`, `downtime_minutes`, `estimated_business_impact_usd`, `root_cause`, `status`

### `infrastructure_costs_monthly.csv`
- Row count: **439**
- Columns: `month`, `aws_service`, `cost_usd`, `environment`, `cost_category`

### `plans.csv`
- Row count: **3**
- Columns: `plan_type`, `base_mrr`, `included_seats`, `seat_price`, `included_storage_gb`, `included_api_calls`, `target_cost_ratio`

### `product_usage_monthly.csv`
- Row count: **39,561**
- Columns: `month`, `customer_id`, `feature_name`, `eligible_flag`, `feature_used_flag`, `seat_count`, `active_users`, `seat_utilization_pct`, `login_count`, `workflow_runs`, `collaboration_actions`, `dashboard_views`, `exports_count`, `export_gb`, `api_calls`, `storage_gb`, `compute_minutes`, `ai_tokens_million`, `athena_scanned_gb`, `analytics_queries`, `admin_actions`

### `subscriptions_monthly.csv`
- Row count: **6,307**
- Columns: `month`, `customer_id`, `plan_type`, `seat_count`, `base_mrr_usd`, `discount_pct`, `mrr_usd`, `arr_usd`, `contract_type`, `renewal_month`, `subscription_status`

### `support_tickets_monthly.csv`
- Row count: **6,307**
- Columns: `month`, `customer_id`, `ticket_count`, `high_severity_tickets`, `avg_resolution_hours`, `csat_score`

## Curated datasets

### `anomalies.csv`
- Row count: **68**
- Columns: `month`, `entity_type`, `entity_name`, `metric_name`, `metric_value`, `rolling_mean`, `deviation_pct`, `severity`

### `customer_monthly.csv`
- Row count: **6,307**
- Columns: `month`, `customer_id`, `plan_type`, `seat_count`, `base_mrr_usd`, `discount_pct`, `mrr_usd`, `arr_usd`, `contract_type_x`, `renewal_month`, `subscription_status`, `company_name`, `industry`, `company_size_segment`, `region`, `country`, `signup_date`, `churn_date`, `initial_plan`, `contract_type_y`, `account_owner`, `risk_profile`, `power_user_flag`, `underpriced_flag`, `planned_upgrade_month`, `eligible_features`, `adopted_features`, `active_users`, `login_count`, `workflow_runs`, `api_calls`, `storage_gb`, `compute_minutes`, `ai_tokens_million`, `athena_scanned_gb`, `feature_adoption_rate`, `direct_cloud_cost_usd`, `ticket_count`, `high_severity_tickets`, `avg_resolution_hours`, `csat_score`, `shared_overhead_usd`, `shared_cost_allocation_usd`, `allocated_cloud_cost_usd`, `cost_to_revenue_ratio`, `estimated_gross_margin_pct`, `cost_per_active_user_usd`, `margin_risk_tier`, `customer_health_score`, `revenue_at_risk_usd`

### `data_quality_report.csv`
- Row count: **19**
- Columns: `table_name`, `check_name`, `status`, `observed_value`, `expected_rule`

### `executive_monthly.csv`
- Row count: **18**
- Columns: `month`, `mrr_usd`, `active_customers`, `total_active_users`, `revenue_at_risk_usd`, `avg_customer_health_score`, `margin_risk_customers`, `total_cloud_cost_usd`, `budget_usd`, `actual_cost_usd`, `forecast_cost_usd`, `variance_usd`, `variance_pct`, `incident_count`, `downtime_minutes`, `estimated_business_impact_usd`, `arr_run_rate_usd`, `cloud_cost_to_revenue_ratio`, `estimated_gross_margin_pct`, `cost_per_active_customer_usd`, `cost_per_active_user_usd`, `mrr_growth_pct`, `cloud_cost_growth_pct`

### `feature_monthly.csv`
- Row count: **150**
- Columns: `month`, `feature_name`, `eligible_customers`, `active_users`, `workflow_runs`, `api_calls`, `storage_gb`, `compute_minutes`, `ai_tokens_million`, `athena_scanned_gb`, `adopted_customers`, `feature_adoption_rate`, `feature_cloud_cost_usd`, `product_area`, `release_date`, `minimum_plan`, `primary_aws_service`, `primary_usage_metric`, `business_value`, `cost_per_active_user_usd`, `cost_per_adopted_customer_usd`, `cost_share_pct`, `mom_cost_growth_pct`, `mom_adoption_growth_pct`, `economics_quadrant`

### `recommendations.csv`
- Row count: **8**
- Columns: `recommendation_id`, `as_of_month`, `category`, `issue`, `evidence`, `recommended_action`, `owner`, `effort`, `implementation_risk`, `estimated_monthly_savings_usd`, `estimated_monthly_revenue_uplift_usd`, `estimated_total_monthly_impact_usd`, `confidence`, `priority_score`, `status`

### `service_environment_monthly.csv`
- Row count: **439**
- Columns: `month`, `aws_service`, `environment`, `cost_category`, `cost_usd`, `monthly_cost_share_pct`, `budget_usd`, `variance_usd`, `variance_pct`

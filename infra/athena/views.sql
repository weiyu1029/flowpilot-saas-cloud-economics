CREATE OR REPLACE VIEW flowpilot_cloud_economics.latest_margin_risk_customers AS
SELECT *
FROM flowpilot_cloud_economics.customer_monthly
WHERE month = (SELECT max(month) FROM flowpilot_cloud_economics.customer_monthly)
  AND margin_risk_tier = 'Margin Risk';

CREATE OR REPLACE VIEW flowpilot_cloud_economics.latest_feature_economics AS
SELECT *
FROM flowpilot_cloud_economics.feature_monthly
WHERE month = (SELECT max(month) FROM flowpilot_cloud_economics.feature_monthly);

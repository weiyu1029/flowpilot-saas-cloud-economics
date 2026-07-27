# FlowPilot SaaS 產品使用量與雲端成本最佳化平台

這是一個完整的 **Business Analyst + Product Analytics + FinOps + AWS + Streamlit** 作品集專案。所有資料都是可重現的 synthetic data，不包含真實客戶資料、AWS 帳單或憑證。

## 專案解決什麼問題？

虛構的 B2B SaaS 公司 FlowPilot 發現雲端成本持續成長，但 Product、Finance、Customer Success 與 Engineering 看的是不同數字，無法一起回答：

- 哪些產品功能最花錢？
- 哪些功能成本高、adoption 卻不理想？
- 哪些客戶使用大量雲端資源，但 MRR 不足以支撐成本？
- 哪些 AWS 服務、環境或月份出現異常成本？
- 公司應該優化架構、調整 retention policy，還是重新定價？

## 作品內容

- 480 個 synthetic customers
- 18 個月 subscription、product usage、support、budget、AWS-style cost 資料
- 121K+ feature/customer/service cost allocation rows
- CSV 與 Parquet 兩種資料格式
- 可重複執行的 Python data pipeline
- 7 個 Streamlit 決策頁面
- 19 項資料品質檢查，全部通過
- AWS S3、Lambda／Glue、Glue Catalog、Athena、CloudWatch、SNS、IAM、Budgets 參考架構
- Athena SQL、CloudFormation、Lambda、IAM policy 範例
- Pytest 與 GitHub Actions CI
- BRD、stakeholder map、user stories、KPI dictionary、ADR、interview guide、demo script

## 最新 synthetic business snapshot（2026 年 6 月）

| 指標 | 結果 |
|---|---:|
| MRR | $751,800 |
| Cloud cost | $178,102 |
| Cost-to-revenue ratio | 23.7% |
| Estimated infrastructure gross margin | 76.3% |
| Margin-risk customers | 88 |
| MRR at risk | $273,050 |
| Monthly optimization opportunity | $64,708 |

## 本機啟動

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 重建完整資料

```bash
python scripts/run_pipeline.py
```

## 執行測試

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Streamlit Community Cloud 部署

1. 把此資料夾推送到 GitHub public repository。
2. 登入 Streamlit Community Cloud，連接 GitHub。
3. 選擇 repository、`main` branch，以及 root 下的 `streamlit_app.py`。
4. Python version 選 3.12。
5. 部署。這個 deterministic 版本不需要任何 secrets。

更詳細的部署說明：[`docs/streamlit_deployment.md`](docs/streamlit_deployment.md)

## 重要聲明

- 所有數字皆為 synthetic scenario，不是即時 AWS 價格。
- Gross margin 只扣除示範性的 infrastructure cost，不是正式會計毛利。
- Public Streamlit 版不需要 AWS credentials。
- 不要把 `.pem`、AWS access key、API key 或 `secrets.toml` 提交到 GitHub。

完整英文 GitHub 作品集說明請看 [`README.md`](README.md)。

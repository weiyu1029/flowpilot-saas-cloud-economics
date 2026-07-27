# Streamlit Community Cloud Deployment

## Repository requirements
- The repository contains `streamlit_app.py` at the root.
- Python dependencies are pinned in `requirements.txt`.
- The app requires no secrets in its current deterministic mode.
- Curated datasets are checked into `data/curated/`.

## Deploy
1. Push this repository to GitHub.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Choose **Create app**.
4. Select repository `weiyu1029/flowpilot-saas-cloud-economics`, branch `main`, and entrypoint `streamlit_app.py`.
5. Choose a unique app URL, for example `flowpilot-cloud-economics`.
6. Deploy and wait for dependency installation.
7. Open **Manage app → Logs** if startup fails.

## Updates
Push changes to the selected GitHub branch. Community Cloud redeploys the app from the updated repository.

## Secrets
The current app does not need secrets. Future Claude/OpenAI/AWS integrations should be stored in Streamlit Secrets and read with `st.secrets`; never commit them.

## Troubleshooting
- `ModuleNotFoundError`: verify the package is listed in `requirements.txt`.
- Missing data: preserve the repository-relative `data/curated/` paths.
- Memory pressure: keep filters and cached data loading; do not load raw 100K+ row datasets unless required.
- Python incompatibility: set an available Python version in Advanced settings and keep package versions compatible.
- Private repository not visible: reconnect GitHub permissions and confirm repository access.


## Current repository
The project is staged in the connected empty repository `weiyu1029/flowpilot-saas-cloud-economics`. Rename it to `flowpilot-saas-cloud-economics` before public portfolio sharing if desired.

# Deployment Handoff

## Recommended repository

Create a public GitHub repository named:

```text
flowpilot-saas-cloud-economics
```

The target public repository is `weiyu1029/flowpilot-saas-cloud-economics`. Clone it first, then copy this complete portfolio into the clone so the existing Git history is preserved.

## Push from macOS Terminal

After unzipping this project and opening Terminal in the project directory:

```bash
git init
git add .
git commit -m "Build FlowPilot SaaS cloud economics portfolio"
git branch -M main
git remote add origin https://github.com/weiyu1029/flowpilot-saas-cloud-economics.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud

Choose:

- Repository: `weiyu1029/flowpilot-saas-cloud-economics`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: `3.12`
- Suggested subdomain: `flowpilot-cloud-economics`

The app requires no secrets.

## After deployment

1. Copy the final `.streamlit.app` URL.
2. Add the Streamlit badge to `README.md`.
3. Update LinkedIn and resume with the live app and GitHub URL.
4. Verify all seven pages on desktop and mobile.

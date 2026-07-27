# Publish FlowPilot to GitHub

Target repository: `weiyu1029/flowpilot-saas-cloud-economics`

Because the repository already exists, the safest workflow is to clone it, copy this complete portfolio into the clone, review the changes, commit, and push.

## Recommended Mac workflow

```bash
mkdir -p ~/Documents/GitHub
cd ~/Documents/GitHub
git clone https://github.com/weiyu1029/flowpilot-saas-cloud-economics.git
```

Copy the extracted project contents—including hidden folders such as `.github` and `.streamlit`—into the cloned repository. Preserve the clone's `.git` directory.

Then run:

```bash
cd ~/Documents/GitHub/flowpilot-saas-cloud-economics
git status
git add -A
git diff --cached --check
git commit -m "Add complete FlowPilot SaaS cloud economics portfolio"
git pull --rebase origin main
git push -u origin main
```

Never commit `.pem` private keys, `.env`, real `secrets.toml`, AWS access keys, passwords, or customer data.

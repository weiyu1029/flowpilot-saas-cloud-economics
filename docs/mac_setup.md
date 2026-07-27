# macOS Setup and Publish

## Run locally with one double-click
1. Unzip the project.
2. Control-click `RUN_LOCAL_MAC.command` and choose **Open** the first time.
3. macOS creates a virtual environment, installs runtime packages, and opens the Streamlit app.

You can also use Terminal:

```bash
cd ~/Downloads/flowpilot-saas-cloud-economics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Publish and open Streamlit deployment
1. Create or rename a GitHub repository to `flowpilot-saas-cloud-economics`.
2. Double-click `PUBLISH_AND_OPEN_STREAMLIT_MAC.command`.
3. Paste the GitHub HTTPS repository URL.
4. Complete any GitHub authentication prompt.
5. The script opens Streamlit Community Cloud after the push succeeds.
6. Select branch `main` and file `streamlit_app.py`.

The current app needs no secrets.

# Spin Dashboard

Streamlit dashboard for customer value, personas, Flip-Out targets, and model performance.

## Run locally (Windows)

From this directory, create and activate a virtual environment, install dependencies, and start the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard opens at the local URL printed by Streamlit, usually `http://localhost:8501`.

## Deploy from GitHub

Deploy this repository with Streamlit Community Cloud and set **Main file path** to:

```text
spin_dashboard/app.py
```

The app's data files are in `spin_dashboard/data/`; keep that directory alongside `app.py`. Dependencies are listed in `spin_dashboard/requirements.txt`.

`data/target_list.csv` contains synthetic demo rows, not a real contact list. The Target list tab displays a demo-only warning; do not use the sample data for real campaigns.

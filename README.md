# Spin by OXXO - Dashboard

Decision-support dashboard in Streamlit built on top of customer segmentation and Flip-Out propensity modeling for 50,000 Spin by OXXO users
- `dashboard_inputs/`: CSV input files used for the dashboard.
- `Evidence_4_Dashboard.ipynb`: Google Colab notebook that processes the data and launches the Streamlit app.

## Tabs Included
- **Overview:** Headline KPIs, user vs. revenue/CLTV split, commission sliders, and key insights.
- **Personas:** Customer profiles and comparison views (Radar, Heatmap, Side by side).
- **Target list:** Filtering by persona, decile, and capacity to select users and export a CSV.
- **Model:** Active model metrics, SHAP drivers, persona performance, and experiment iterations.

## How to Run
1. Open `Evidence_4_Dashboard.ipynb` in **Google Colab**.
2. Ensure the project folder is accessible under **MyDrive** (`/content/drive/MyDrive/...`).
3. Run the cells in order to install dependencies, prepare the data, generate `app.py` inside `spin_dashboard`, and launch the Streamlit dashboard.


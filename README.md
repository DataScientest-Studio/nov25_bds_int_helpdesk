# Help Desk Performance Appraisal System

Supervised & unsupervised analysis and scoring of help desk employee performance based on ticket data.

## Data Source

Abdellatif, Mohammad (2025), "Help Desk Tickets", Mendeley Data, V2, doi: 10.17632/btm76zndnt.2

## Project Structure

```
data/
  raw/          - Original dataset
  processed/    - Derived features and clustering results
models/         - Trained ML models (joblib)
src/            - Data processing, scoring and clustering scripts
streamlit_app/  - Interactive dashboard
```

## Models

- `optimized_scorer.joblib` - Optuna-optimized Q-Score classifier (XGBoost + LightGBM)
- `q_score_model.joblib`    - Base ensemble Q-Score classifier (RF + XGBoost + LightGBM)
- `kmeans_model.joblib`     - K-Means clustering model (k=4)
- `scaler.joblib`           - RobustScaler for clustering pipeline

## Requirements

See `requirements.txt`. Install with:

```
pip install -r requirements.txt
```

## Dashboard

Start the Streamlit dashboard:

```
python -m streamlit run streamlit_app/app.py --server.port 8501
```
or Streamlit directly:

https://aen3amavkn3bjffcaidqfz.streamlit.app/

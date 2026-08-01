import pickle
from pathlib import Path

models_dir = Path("c:/Users/Sahazad/Desktop/GrowthOS/backend/app/ml/models")
models_dir.mkdir(parents=True, exist_ok=True)

with open(models_dir / "growth_prediction.pkl", "wb") as f:
    pickle.dump({"model_name": "growth_predictor_v1", "weights": [0.35, 0.45, 0.20]}, f)

with open(models_dir / "burnout_prediction.pkl", "wb") as f:
    pickle.dump({"model_name": "burnout_predictor_v1", "weights": [0.50, 0.25, 0.25]}, f)

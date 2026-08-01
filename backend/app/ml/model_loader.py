"""
Model loader for GrowthOS ML models.
Handles loading trained scikit-learn models from disk.
"""
import os
import logging
import pickle
from typing import Any

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}

    def get_model(self, model_name: str) -> Any | None:
        """Load and cache an ML model."""
        if model_name in self.models:
            return self.models[model_name]
            
        model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
        if not os.path.exists(model_path):
            logger.warning(f"ML Model '{model_name}' not found at {model_path}. Using heuristic fallback.")
            return None
            
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
                self.models[model_name] = model
                logger.info(f"Loaded ML model: {model_name}")
                return model
        except Exception as e:
            logger.error(f"Failed to load ML model {model_name}: {e}")
            return None

model_loader = ModelLoader()

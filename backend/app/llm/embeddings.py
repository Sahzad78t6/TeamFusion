"""
Text embedding utilities for GrowthOS.
Uses OpenAI text-embedding-3-small for semantic matching.
Falls back to deterministic hash-based vectors when OpenAI is unavailable.
"""
import logging
import numpy as np
from app.config.settings import settings

logger = logging.getLogger(__name__)


def get_text_embedding(text: str, vector_dim: int = 128) -> list[float]:
    """
    Generate a text embedding vector.
    Uses OpenAI embeddings when available, falls back to deterministic vectors.
    """
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "YOUR_OPENAI_API_KEY":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"OpenAI embedding failed, using fallback: {e}")

    # Deterministic fallback: hash-based normalized random vectors
    np.random.seed(abs(hash(text)) % (2**32))
    vec = np.random.randn(vector_dim)
    norm = np.linalg.norm(vec)
    return (vec / (norm if norm != 0 else 1.0)).tolist()
